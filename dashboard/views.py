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
from dashboard.models import Document, Shingle, Student, Doctype, School, Topic
from sklearn.feature_extraction.text import TfidfVectorizer
from PIL import Image, ImageFilter
import fitz
from django.core.files.storage import default_storage

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

stop_words = ("able", "about", "above", "abroad", "according", "accordingly", "across", "actually", "adj", "after",
              "afterwards", "again", "against", "ago", "ahead", "ain't", "all", "allow", "allows", "almost", "alone",
              "along", "alongside", "already", "also", "although", "always", "am", "amid", "amidst", "among", "amongst",
              "an", "and", "another", "any", "anybody", "anyhow", "anyone", "anything", "anyway", "anyways", "anywhere",
              "apart", "appear", "appreciate", "appropriate", "are", "aren't", "around", "as", "a's", "aside", "ask",
              "asking", "associated", "at", "available", "away", "awfully", "back", "backward", "backwards", "be",
              "became",
              "because", "become", "becomes", "becoming", "been", "before", "beforehand", "begin", "behind", "being",
              "believe", "below", "beside", "besides", "best", "better", "between", "beyond", "both", "brief", "but",
              "by",
              "came", "can", "cannot", "cant", "can't", "caption", "cause", "causes", "certain", "certainly", "changes",
              "clearly", "c'mon", "co", "co.", "com", "come", "comes", "concerning", "consequently", "consider",
              "considering", "contain", "containing", "contains", "corresponding", "could", "couldn't", "course", "c's",
              "currently", "dare", "daren't", "definitely", "described", "despite", "did", "didn't", "different",
              "directly",
              "do", "does", "doesn't", "doing", "done", "don't", "down", "downwards", "during", "each", "edu", "eg",
              "eight",
              "eighty", "either", "else", "elsewhere", "end", "ending", "enough", "entirely", "especially", "et", "etc",
              "even", "ever", "evermore", "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly",
              "example", "except", "fairly", "far", "farther", "few", "fewer", "fifth", "first", "five", "followed",
              "following", "follows", "for", "forever", "former", "formerly", "forth", "forward", "found", "four",
              "from",
              "further", "furthermore", "get", "gets", "getting", "given", "gives", "go", "goes", "going", "gone",
              "got",
              "gotten", "greetings", "had", "hadn't", "half", "happens", "hardly", "has", "hasn't", "have", "haven't",
              "having", "he", "he'd", "he'll", "hello", "help", "hence", "her", "here", "hereafter", "hereby", "herein",
              "here's", "hereupon", "hers", "herself", "he's", "hi", "him", "himself", "his", "hither", "hopefully",
              "how",
              "howbeit", "however", "hundred", "i'd", "ie", "if", "ignored", "i'll", "i'm", "immediate", "in",
              "inasmuch",
              "inc", "inc.", "indeed", "indicate", "indicated", "indicates", "inner", "inside", "insofar", "instead",
              "into",
              "inward", "is", "isn't", "it", "it'd", "it'll", "its", "it's", "itself", "i've", "just", "k", "keep",
              "keeps",
              "kept", "know", "known", "knows", "last", "lately", "later", "latter", "latterly", "least", "less",
              "lest",
              "let", "let's", "like", "liked", "likely", "likewise", "little", "look", "looking", "looks", "low",
              "lower",
              "ltd", "made", "mainly", "make", "makes", "many", "may", "maybe", "mayn't", "me", "mean", "meantime",
              "meanwhile", "merely", "might", "mightn't", "mine", "minus", "miss", "more", "moreover", "most", "mostly",
              "mr", "mrs", "much", "must", "mustn't", "my", "myself", "name", "namely", "nd", "near", "nearly",
              "necessary",
              "need", "needn't", "needs", "neither", "never", "neverf", "neverless", "nevertheless", "new", "next",
              "nine",
              "ninety", "no", "nobody", "non", "none", "nonetheless", "noone", "no-one", "nor", "normally", "not",
              "nothing",
              "notwithstanding", "novel", "now", "nowhere", "obviously", "of", "off", "often", "oh", "ok", "okay",
              "old",
              "on", "once", "one", "ones", "one's", "only", "onto", "opposite", "or", "other", "others", "otherwise",
              "ought", "oughtn't", "our", "ours", "ourselves", "out", "outside", "over", "overall", "own", "particular",
              "particularly", "past", "per", "perhaps", "placed", "please", "plus", "possible", "presumably",
              "probably",
              "provided", "provides", "que", "quite", "qv", "rather", "rd", "re", "really", "reasonably", "recent",
              "recently", "regarding", "regardless", "regards", "relatively", "respectively", "right", "round", "said",
              "same", "saw", "say", "saying", "says", "second", "secondly", "see", "seeing", "seem", "seemed",
              "seeming",
              "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously", "seven", "several",
              "shall",
              "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "since", "six", "so", "some",
              "somebody",
              "someday", "somehow", "someone", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon",
              "sorry", "specified", "specify", "specifying", "still", "sub", "such", "sup", "sure", "take", "taken",
              "taking", "tell", "tends", "th", "than", "thank", "thanks", "thanx", "that", "that'll", "thats", "that's",
              "that've", "the", "their", "theirs", "them", "themselves", "then", "thence", "there", "thereafter",
              "thereby",
              "there'd", "therefore", "therein", "there'll", "there're", "theres", "there's", "thereupon", "there've",
              "these", "they", "they'd", "they'll", "they're", "they've", "thing", "things", "think", "third", "thirty",
              "this", "thorough", "thoroughly", "those", "though", "three", "through", "throughout", "thru", "thus",
              "till",
              "to", "together", "too", "took", "toward", "towards", "tried", "tries", "truly", "try", "trying", "t's",
              "twice", "two", "un", "under", "underneath", "undoing", "unfortunately", "unless", "unlike", "unlikely",
              "until", "unto", "up", "upon", "upwards", "us", "use", "used", "useful", "uses", "using", "usually", "v",
              "value", "various", "versus", "very", "via", "viz", "vs", "want", "wants", "was", "wasn't", "way", "we",
              "we'd", "welcome", "well", "we'll", "went", "were", "we're", "weren't", "we've", "what", "whatever",
              "what'll",
              "what's", "what've", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein",
              "where's", "whereupon", "wherever", "whether", "which", "whichever", "while", "whilst", "whither", "who",
              "who'd", "whoever", "whole", "who'll", "whom", "whomever", "who's", "whose", "why", "will", "willing",
              "wish",
              "with", "within", "without", "wonder", "won't", "would", "wouldn't", "yes", "yet", "you", "you'd",
              "you'll",
              "your", "you're", "yours", "yourself", "yourselves", "you've", "zero", "a", "how's", "i", "when's",
              "why's",
              "b", "c", "d", "e", "f", "g", "h", "j", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "uucp", "w",
              "x",
              "y", "z", "I", "www", "amount", "bill", "bottom", "call", "computer", "con", "couldnt", "cry", "de",
              "describe", "detail", "due", "eleven", "empty", "fifteen", "fifty", "fill", "find", "fire", "forty",
              "front",
              "full", "give", "hasnt", "herse", "himse", "interest", "itse”", "mill", "move", "myse”", "part", "put",
              "show",
              "side", "sincere", "sixty", "system", "ten", "thick", "thin", "top", "twelve", "twenty", "abst",
              "accordance",
              "act", "added", "adopted", "affected", "affecting", "affects", "ah", "announce", "anymore", "apparently",
              "approximately", "aren", "arent", "arise", "auth", "beginning", "beginnings", "begins", "biol", "briefly",
              "ca", "date", "ed", "effect", "et-al", "ff", "fix", "gave", "giving", "heres", "hes", "hid", "home", "id",
              "im", "immediately", "importance", "important", "index", "information", "invention", "itd", "keys", "kg",
              "km",
              "largely", "lets", "line", "'ll", "means", "mg", "million", "ml", "mug", "na", "nay", "necessarily",
              "nos",
              "noted", "obtain", "obtained", "omitted", "ord", "owing", "page", "pages", "poorly", "possibly",
              "potentially",
              "pp", "predominantly", "present", "previously", "primarily", "promptly", "proud", "quickly", "ran",
              "readily",
              "ref", "refs", "related", "research", "resulted", "resulting", "results", "run", "sec", "section", "shed",
              "shes", "showed", "shown", "showns", "shows", "significant", "significantly", "similar", "similarly",
              "slightly", "somethan", "specifically", "state", "states", "stop", "strongly", "substantially",
              "successfully",
              "sufficiently", "suggest", "thered", "thereof", "therere", "thereto", "theyd", "theyre", "thou",
              "thoughh",
              "thousand", "throug", "til", "tip", "ts", "ups", "usefully", "usefulness", "'ve", "vol", "vols", "wed",
              "whats", "wheres", "whim", "whod", "whos", "widely", "words", "world", "youd", "youre", "study",
              "research",
              "paper", "article", "author", "introduction", "conclusion", "discussion",
              "results", "methods", "methodology", "findings", "data", "information", "analysis", "review",
              "references", "figures", "tables", "appendix", "supplementary", "supporting", "materials")


def index(request):
    context = {'segment': 'dashboard'}
    if request.user.is_authenticated:
        context['user'] = request.user
        if request.user.student.school is None:
            return redirect('account:complete-profile')
        if request.user.is_superuser:
            students = Student.objects.all()
            files = Document.objects.all()
            schools = School.objects.all().order_by('name')
            topics = Topic.objects.all().order_by('name')
            doctypes = Doctype.objects.all().order_by('name')
            context['students'] = students
            context['files'] = files
            context['schools'] = schools
            context['topics'] = topics
            context['doctypes'] = doctypes
            return render(request, 'dashboard/pages/tables.html', context=context)
        return render(request, 'dashboard/pages/dashboard.html', context=context)
    else:
        return redirect('home')


def save_info(request, document_id):
    if request.method == 'POST':
        info = request.POST.get('info')
        title = request.POST.get('title')
        course_id = request.POST.get('course')
        doctype_id = request.POST.get('doctype')
        uni_id = request.POST.get('uni')
        course = Topic.objects.get(id=course_id)
        doctype = Doctype.objects.get(id=doctype_id)
        uni = School.objects.get(id=uni_id)

        # Update or create the FileInfo object
        Document.objects.update_or_create(
            id=document_id,
            defaults={
                'info': info,
                'title': title,
                'course': course,
                'doctype': doctype,
                'uni': uni
            }
        )
        messages.success(request,
                         "Document Informations Updated Successfully!")
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
    doctypes = Doctype.objects.all().order_by('name')
    schools = School.objects.all().order_by('name')
    topics = Topic.objects.all().order_by('name')
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
        'schools': schools,
        'topics': topics
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
        messages.success(request,
                         "File Deleted Succesfully!")
    return redirect(request.META.get('HTTP_REFERER'))


def delete_school(request, school_id):
    if request.user.is_superuser:
        school = get_object_or_404(School, id=school_id)
        if request.method == 'POST':
            school.delete()
            messages.success(request,
                             "School Deleted Succesfully!")
        return redirect(request.META.get('HTTP_REFERER'))


def delete_doct(request, doct_id):
    if request.user.is_superuser:
        doct = get_object_or_404(Doctype, id=doct_id)
        if request.method == 'POST':
            doct.delete()
        messages.success(request,
                         "Document Type Deleted Succesfully!")
        return redirect(request.META.get('HTTP_REFERER'))


def delete_subject(request, subject_id):
    if request.user.is_superuser:
        subject = get_object_or_404(Topic, id=subject_id)
        if request.method == 'POST':
            subject.delete()
            messages.success(request,
                             "Subject Deleted Succesfully!")
        return redirect(request.META.get('HTTP_REFERER'))


def add_school(request):
    if request.method == 'POST':
        school_name = request.POST.get('school_name')
        school = School.objects.create(name=school_name)
    messages.success(request,
                     "School Added Succesfully!")
    return redirect(request.META.get('HTTP_REFERER'))


def add_subject(request):
    if request.method == 'POST':
        subject_name = request.POST.get('subject_name')
        subject_coeff = request.POST.get('subject_coeff')
        subject = Topic.objects.create(name=subject_name, coef=subject_coeff)
        messages.success(request,
                         "Subject Added Succesfully!")
    return redirect(request.META.get('HTTP_REFERER'))


def update_subject(request, subject_id):
    if request.method == 'POST':
        subject_name = request.POST.get('subject_name')
        subject_coeff = request.POST.get('subject_coeff')
        Topic.objects.update_or_create(
            id=subject_id,
            defaults={
                'name': subject_name,
                'coef': subject_coeff
            }
        )
        messages.success(request,
                         "Subject Updated Succesfully!")
    return redirect(request.META.get('HTTP_REFERER'))


def add_doct(request):
    if request.method == 'POST':
        doct_name = request.POST.get('doct_name')
        doct = Doctype.objects.create(name=doct_name)
        messages.success(request, "Document Type Added Succesfully!")
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


def calculate_points(coeff, length):
    base_points = 10
    subject_relevance = 20
    length_relevance = 0.001
    points = base_points + subject_relevance * coeff + length_relevance * length
    return int(points)


@login_required
def upload_file(request):
    media_path = os.path.join(settings.MEDIA_ROOT)

    if request.method == 'POST':
        user = request.user.student
        file = request.FILES.get('file')
        info = request.POST.get('info')
        title = request.POST.get('title')
        course_id = request.POST.get('course')
        doctype_id = request.POST.get('doctype')
        uni_id = request.POST.get('uni')
        course = Topic.objects.get(id=course_id)
        doctype = Doctype.objects.get(id=doctype_id)
        uni = School.objects.get(id=uni_id)
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
            coeff = float(course.coef)
            awarded_points = calculate_points(coeff, length)
            # Encode the pickled data to a base64 string
            b64_pickled_shingles = base64.b64encode(pickled_shingles).decode()
            existing_documents = Document.objects.all()
            if is_duplicate(user, shingles):
                messages.warning(request, 'File is too similar to an existing file.')
                return redirect(request.META.get('HTTP_REFERER'))
            cost = awarded_points + 10
            # Create Document and Shingle objects
            document = Document.objects.create(user=user, file_field=file, info=info, title=title, course=course,
                                               doctype=doctype, uni=uni, text=text, lang=lang,
                                               keywords=keywords, cost=cost)
            student = document.user
            student.points_field += awarded_points
            student.save()

            Shingle.objects.create(document=document, pickled_shingles=b64_pickled_shingles)
            # Success message and redirection logic
            messages.success(request,
                             f'File uploaded successfully! {awarded_points} points gained')
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
    filtered_tokens = [token for token in lower_tokens if token not in stop_words]
    tagged_tokens = nltk.pos_tag(filtered_tokens)
    refiltered_tokens = [token for token, tag in tagged_tokens if tag in ['NN', 'VB', 'JJ', 'RB']]
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in refiltered_tokens]
    word_counts = Counter(lemmatized_tokens)
    top_keywords = word_counts.most_common(50)  # Extract top 50 most frequent words
    print("Top Keywords:")
    joined_kw = ""
    for keyword, count in top_keywords:
        print(f"- {keyword} ({count})")
        joined_kw += keyword + " "
    return joined_kw


def search(request):
    query = request.GET.get('query')
    if query:
        vector = SearchVector(('title', 'C'), ('keywords', 'B'), ('info', 'B'), ('course__name', 'B'))
        q = SearchQuery(vector)
        files = Document.objects.exclude(user=request.user.student).filter(
            Q(title__icontains=query) | Q(info__icontains=query) | Q(course__name__icontains=query) | Q(
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


def profile(request):
    if request.user.is_authenticated:
        user = request.user.student
        context = {'user': user}
        return render(request, 'dashboard/pages/profile.html', context=context)
    return redirect('home')
