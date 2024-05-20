import base64
import hashlib
import nltk
import numpy as np
import os
import pdfplumber
import pickle
import re
import subprocess
import uuid
from collections import Counter
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from io import BytesIO
from langdetect import detect
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from PyPDF2 import PdfReader, PdfWriter
from dashboard.models import Document, Shingle, Student, Doctype, School
from sklearn.feature_extraction.text import TfidfVectorizer
from PIL import Image, ImageFilter
import fitz
from django.core.files.storage import default_storage

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')


def index(request):
    context = {'segment': 'dashboard'}
    if request.user.is_authenticated:
        context['user'] = request.user
        if request.user.is_superuser:
            students = Student.objects.all()
            files = Document.objects.all()
            context['students'] = students
            context['files'] = files

            return render(request, 'dashboard/pages/tables.html', context=context)
        return render(request, 'dashboard/pages/dashboard.html', context=context)
    else:
        return redirect('home')


def save_info(request, document_id):
    if request.method == 'POST':
        info = request.POST.get('info')
        title = request.POST.get('title')
        course = request.POST.get('course')
        subject = request.POST.get('subject')
        doctype = request.POST.get('doctype')
        uni = request.POST.get('uni')

        # Update or create the FileInfo object
        Document.objects.update_or_create(
            id=document_id,
            defaults={
                'info': info,
                'title': title,
                'course': course,
                'subject': subject,
                'doctype': doctype,
                'uni': uni
            }
        )
    return redirect('dashboard:file_manager')
    # return redirect(request.META.get('HTTP_REFERER'))


def get_breadcrumbs(request):
    path_components = [component for component in request.path.split("/") if component]
    breadcrumbs = []
    url = ''

    for component in path_components:
        url += f'/{component}'
        if component == "file-manager":
            component = "media"
        breadcrumbs.append({'name': component, 'url': url})

    return breadcrumbs


@login_required
def file_manager(request, directory=''):
    media_path = os.path.join(settings.MEDIA_ROOT)
    directories = generate_nested_directory(media_path, media_path)
    selected_directory = directory
    user = request.user
    doctypes = Doctype.objects.all()
    schools = School.objects.all()
    if user.is_superuser:
        files = Document.objects.all()
    else:
        files = Document.objects.filter(user=user.student)

    breadcrumbs = "My Documents"

    context = {
        'files': files,
        'segment': 'Library',
        'breadcrumbs': breadcrumbs,
        'doctypes': doctypes,
        'schools': schools
    }
    return render(request, 'dashboard/pages/file-manager.html', context)


@login_required
def wallet(request):
    user = request.user.student
    points = user.points_field
    context = {
        'points': points,
        'segment': 'wallet',
    }
    return render(request, 'dashboard/pages/wallet.html', context)


def generate_nested_directory(root_path, current_path):
    directories = []
    for name in os.listdir(current_path):
        if os.path.isdir(os.path.join(current_path, name)):
            unique_id = str(uuid.uuid4())
            nested_path = os.path.join(current_path, name)
            nested_directories = generate_nested_directory(root_path, nested_path)
            directories.append({'id': unique_id, 'name': name, 'path': os.path.relpath(nested_path, root_path),
                                'directories': nested_directories})
    return directories


def delete_file(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if request.method == 'POST':
        document.delete()
    return redirect(request.META.get('HTTP_REFERER'))


def download_file(request, document_id):
    try:
        document = Document.objects.get(id=document_id)
    except Document.DoesNotExist:
        raise Http404("Document does not exist")

    if document.file_field:
        absolute_file_path = document.file_field.path
        if os.path.exists(absolute_file_path):
            with open(absolute_file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/octet-stream")
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(absolute_file_path)
                return response
    raise Http404("File not found")


@login_required
def upload_file(request):
    media_path = os.path.join(settings.MEDIA_ROOT)

    if request.method == 'POST':
        user = request.user.student
        file = request.FILES.get('file')
        info = request.POST.get('info')
        title = request.POST.get('title')
        course = request.POST.get('course')
        subject = request.POST.get('subject')
        doctype = request.POST.get('doctype')
        uni = request.POST.get('uni')

        # Validate file type
        # if not file.name.endswith('.pdf'):
        #     messages.warning(request, 'Only PDF files are allowed.', extra_tags='file_upload')
        #     return redirect(request.META.get('HTTP_REFERER'))

        try:
            file_path = os.path.join(media_path, file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Extract text using OCR
            text, output_path = extract_text_ocr(file_path)
            shingles = create_shingles(text)
            pickled_shingles = pickle.dumps(shingles)
            keywords = get_keywords(text)
            lang = detect(text)
            length = len(text)
            points_per_unit = 500
            awarded_points = length // points_per_unit
            # Encode the pickled data to a base64 string
            b64_pickled_shingles = base64.b64encode(pickled_shingles).decode()
            existing_documents = Document.objects.all()
            if is_duplicate(user, shingles):
                messages.warning(request, 'File is too similar to an existing file.')
                return redirect(request.META.get('HTTP_REFERER'))

            # Create Document and Shingle objects
            document = Document.objects.create(user=user, file_field=file, info=info, title=title, course=course,
                                               subject=subject, doctype=doctype, uni=uni, text=text, lang=lang,
                                               keywords=keywords, cost=awarded_points)
            student = document.user
            student.points_field += awarded_points
            student.save()

            Shingle.objects.create(document=document, pickled_shingles=b64_pickled_shingles)
            # Success message and redirection logic
            messages.success(request,
                             f'File uploaded successfully! {awarded_points} points gained',
                             extra_tags='file_upload')
            return redirect(request.META.get('HTTP_REFERER'))

        except ValidationError as e:
            messages.error(request, str(e))  # Handle validation errors
            return redirect(request.META.get('HTTP_REFERER'))

        # except Exception as e:  # Catch generic exceptions
        #     print(f"Error uploading file: {e}")
        #     messages.error(request, 'An error occurred during upload. Please try again.')
        #     return redirect(request.META.get('HTTP_REFERER'))

    return redirect(request.META.get('HTTP_REFERER'))


def extract_text_ocr(upload_path):
    file_name = upload_path.split('\\')[-1].replace('.pdf', '') + '_ocr.pdf'
    # output_path = f"media/temp/{file_name}.txt"
    media_path = os.path.join(settings.MEDIA_ROOT)
    output_path = os.path.join(media_path, file_name)
    subprocess.run(["ocrmypdf", "--output-type", "pdf", '--skip-text', upload_path, output_path], check=True)
    text = ''
    with pdfplumber.open(output_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text(x_tolerance=2)
    return text, output_path


def is_duplicate(user, shingles):
    existing_documents = Document.objects.all()
    if existing_documents.exists():
        for ex_doc in existing_documents:
            p_sh = ex_doc.get_pickled_shingles()
            existing_shingles = pickle.loads(p_sh)
            # Calculate Jaccard similarity coefficient between shingles
            similarity_score = calculate_similarity(shingles, existing_shingles)
            print(similarity_score)
            threshold = 0.6
            if similarity_score >= threshold:
                return True
    return False


def create_shingles(text, k=3):
    # Tokenize the text into words
    words = text.split()

    # Create shingles by selecting consecutive sets of words
    shingles = set()
    for i in range(len(words) - k + 1):
        shingle = " ".join(words[i:i + k])
        # Hash the shingle to reduce its size
        hashed_shingle = hashlib.sha1(shingle.encode()).hexdigest()
        shingles.add(hashed_shingle)

    return shingles


def calculate_similarity(shingles1, shingles2):
    jaccard_similarity = len(shingles1.intersection(shingles2)) / len(shingles1.union(shingles2))
    return jaccard_similarity


def get_keywords(text):
    # Remove symbols using regular expression
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = nltk.word_tokenize(text)
    lower_tokens = [token.lower() for token in tokens]
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in lower_tokens if token not in stop_words]
    tagged_tokens = nltk.pos_tag(filtered_tokens)
    refiltered_tokens = [token for token, tag in tagged_tokens if tag in ['NN', 'VB', 'JJ', 'RB']]
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in refiltered_tokens]
    word_counts = Counter(lemmatized_tokens)
    top_keywords = word_counts.most_common(50)  # Extract top 10 most frequent words

    print("Top Keywords:")
    joined_kw = ""
    for keyword, count in top_keywords:
        print(f"- {keyword} ({count})")
        joined_kw += keyword + " "
    return joined_kw


def search(request):
    query = request.GET.get('query')
    if query:
        vector = SearchVector(('title', 'C'), ('keywords', 'B'), ('info', 'B'), ('subject', 'B'))
        q = SearchQuery(vector)
        files = Document.objects.filter(
            Q(title__icontains=query) | Q(info__icontains=query) | Q(subject__icontains=query) | Q(
                keywords__icontains=query)
        )
        for file in files:
            restricted_pdf_view(request, file)
    else:
        files = []
    nb_files = files.count()
    context = {'files': files, 'query': query, 'nb_files': nb_files}

    return render(request, 'dashboard/pages/search.html', context)


def first_page_preview(request, document_id):
    # Fetch document object
    document = Document.objects.get(pk=document_id)
    name = document.file_field.name
    fp = os.path.join(settings.MEDIA_ROOT, name)
    with pdfplumber.open(fp) as pdf:
        first_page = pdf.pages[0]
        # Convert the PDF page to an image
        image = first_page.to_image(resolution=150)  # Adjust resolution as needed

        # Convert the image to PNG format
        image = image.original.convert('RGB')

        # Save the image to a BytesIO buffer
        buffer = BytesIO()
        image.save(buffer, format='PNG')

        # Return the image as an HttpResponse with content type image/png
        return HttpResponse(buffer.getvalue(), content_type='image/png')


def restricted_pdf_view(request, document):
    name = document.file_field.name
    fp = os.path.join(settings.MEDIA_ROOT, name)
    p_name = os.path.splitext(name)[0]
    restricted_pdf = generate_restricted_preview(fp)
    if restricted_pdf:
        restricted_pdf_path = os.path.join(settings.MEDIA_ROOT, f'{p_name}_restricted.pdf')
        # Save the restricted PDF to the media folder
        with open(restricted_pdf_path, 'wb') as f:
            f.write(restricted_pdf)


def generate_restricted_preview(fp):
    try:
        original_pdf_reader = PdfReader(fp)
        total_pages = len(original_pdf_reader.pages)
        if total_pages >= 10:
            num_pages_allowed = 3
        elif total_pages >= 5:
            num_pages_allowed = 2
        else:
            num_pages_allowed = 1

        preview_pdf = BytesIO()
        writer = PdfWriter()
        for page_num in range(total_pages):
            page = original_pdf_reader.pages[page_num]
            if page_num < num_pages_allowed:
                writer.add_page(page)
        writer.write(preview_pdf)
        return preview_pdf.getvalue()
    except Exception as e:
        print(f"Error generating restricted preview: {e}")
        return None
