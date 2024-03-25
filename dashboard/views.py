import base64
import hashlib
import os
import pickle
import subprocess
import uuid
import csv

import pdfplumber
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.files import File
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse, Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.conf import settings
from dashboard.models import Document, Shingle



# Create your views here.

def index(request):
    context = {}
    if request.user.is_authenticated:
        context['user'] = request.user
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
    files = []
    if user.is_superuser:
        files = Document.objects.all()
    else:
        files = Document.objects.filter(user=user)

    breadcrumbs = get_breadcrumbs(request)

    context = {
        'files': files,
        'segment': 'file_manager',
        'breadcrumbs': breadcrumbs
    }
    return render(request, 'dashboard/pages/file-manager.html', context)


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
        user = request.user
        file = request.FILES.get('file')

        # Validate file type
        if not file.name.endswith('.pdf'):
            messages.warning(request, 'Only PDF files are allowed.', extra_tags='file_upload')
            return redirect(request.META.get('HTTP_REFERER'))

        try:
            file_path = os.path.join(media_path, file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Extract text using OCR
            text, output_path = extract_text_ocr(file_path)
            shingles = create_shingles(text)
            pickled_shingles = pickle.dumps(shingles)

            # Encode the pickled data to a base64 string
            b64_pickled_shingles = base64.b64encode(pickled_shingles).decode()
            existing_documents = Document.objects.all()
            if is_duplicate(user, shingles):
                messages.warning(request, 'File is too similar to an existing file.')
                return redirect(request.META.get('HTTP_REFERER'))

            # Create Document and Shingle objects
            document = Document.objects.create(user=user, file_field=file, text=text)
            Shingle.objects.create(document=document, pickled_shingles=b64_pickled_shingles)
            # Success message and redirection logic
            messages.success(request,
                             'File uploaded successfully. Please enter file information to get your points ;)',
                             extra_tags='file_upload')
            redirect_url = f"{request.META.get('HTTP_REFERER')}?file_id={document.id}"
            return HttpResponseRedirect(redirect_url)

        except ValidationError as e:
            messages.error(request, str(e))  # Handle validation errors
            return redirect(request.META.get('HTTP_REFERER'))

        # except Exception as e:  # Catch generic exceptions
        #     print(f"Error uploading file: {e}")
        #     messages.error(request, 'An error occurred during upload. Please try again.')
        #     return redirect(request.META.get('HTTP_REFERER'))

    return redirect(request.META.get('HTTP_REFERER'))


def extract_text_ocr(upload_path):
    file_name = upload_path.split('\\')[-1].replace('.pdf', '')+'_ocr.pdf'
    # output_path = f"media/temp/{file_name}.txt"
    media_path = os.path.join(settings.MEDIA_ROOT)
    output_path = os.path.join(media_path, file_name)
    subprocess.run(["ocrmypdf", '--force-ocr', upload_path, output_path], check=True)
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
