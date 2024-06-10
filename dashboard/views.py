import base64
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from langdetect import detect
from dashboard.models import *
from .utils import *


def index(request):
    context = {}
    if request.user.is_authenticated:
        user = request.user
        context['user'] = user
        if request.user.student.school is None:
            return redirect('account:complete-profile')
        if request.user.is_superuser:
            students = Student.objects.all()
            transactions = Transaction.objects.all().order_by('transaction_date')
            files = Document.objects.all()
            reviews = Review.objects.all()
            context['segment'] = 'Admin Dashboard'
            context['transactions'] = transactions
            context['students'] = students
            context['files'] = files
            context['reviews'] = reviews
            return render(request, 'dashboard/pages/admin_dashboard.html', context=context)
        # return render(request, 'dashboard/pages/dashboard.html', context=context)
        return redirect('dashboard:file_manager')
    else:
        return redirect('home')


@login_required
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
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def file_manager(request):
    media_path = os.path.join(settings.MEDIA_ROOT)
    user = request.user
    if user.is_superuser:
        files = Document.objects.all()
    else:
        files = Document.objects.filter(user=user.student)

    purchased_documents = user.student.purchased_documents.all()

    context = {
        'files': files,
        'purchased_documents': purchased_documents,
        'segment': 'library',
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


@login_required
def delete_file(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if request.method == 'POST':
        document.delete()
        messages.success(request,
                         "File Deleted Succesfully!")
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def delete_school(request, school_id):
    if request.user.is_superuser:
        school = get_object_or_404(School, id=school_id)
        if request.method == 'POST':
            school.delete()
            messages.success(request,
                             "School Deleted Succesfully!")
        return redirect(request.META.get('HTTP_REFERER'))


@login_required
def delete_doct(request, doct_id):
    if request.user.is_superuser:
        doct = get_object_or_404(Doctype, id=doct_id)
        if request.method == 'POST':
            doct.delete()
        messages.success(request,
                         "Document Type Deleted Succesfully!")
        return redirect(request.META.get('HTTP_REFERER'))


@login_required
def delete_subject(request, subject_id):
    if request.user.is_superuser:
        subject = get_object_or_404(Topic, id=subject_id)
        if request.method == 'POST':
            subject.delete()
            messages.success(request,
                             "Subject Deleted Succesfully!")
        return redirect(request.META.get('HTTP_REFERER'))


@login_required
def add_school(request):
    if request.method == 'POST':
        school_name = request.POST.get('school_name')
        school = School.objects.create(name=school_name)
    messages.success(request,
                     "School Added Succesfully!")
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def add_subject(request):
    if request.method == 'POST':
        subject_name = request.POST.get('subject_name')
        subject_coeff = request.POST.get('subject_coeff')
        subject = Topic.objects.create(name=subject_name, coef=subject_coeff)
        messages.success(request,
                         "Subject Added Succesfully!")
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
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


@login_required
def add_doct(request):
    if request.method == 'POST':
        doct_name = request.POST.get('doct_name')
        doct = Doctype.objects.create(name=doct_name)
        messages.success(request, "Document Type Added Succesfully!")
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
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
            Transaction.objects.create(
                user=student,
                document=document,
                transaction_type='upload',
                amount=awarded_points,
            )

            Shingle.objects.create(document=document, pickled_shingles=b64_pickled_shingles)
            # Success message and redirection logic
            messages.success(request,
                             f'File uploaded successfully! {awarded_points} points gained')
            return redirect(request.META.get('HTTP_REFERER'))

        except ValidationError as e:
            messages.error(request, str(e))  # Handle validation errors
            return redirect(request.META.get('HTTP_REFERER'))

    return redirect(request.META.get('HTTP_REFERER'))


def profile(request):
    if request.user.is_authenticated:
        return render(request, 'dashboard/pages/profile.html')
    return redirect('home')


def search(request):
    purchased_documents = request.user.student.purchased_documents.all()
    query = request.GET.get('query')
    if query:
        vector = SearchVector(('title', 'C'), ('keywords', 'B'), ('info', 'B'), ('course__name', 'B'))
        q = SearchQuery(vector)
        files = (Document.objects.exclude(user=request.user.student).filter(
            Q(title__icontains=query) | Q(info__icontains=query) | Q(course__name__icontains=query) | Q(
                keywords__icontains=query)
        ))
        for file in files:
            restricted_pdf_view(request, file)
    else:
        files = []

    nb_files = files.count()
    context = {'files': files, 'query': query, 'nb_files': nb_files, 'purchased_documents': purchased_documents}

    return render(request, 'dashboard/pages/search.html', context)


@login_required
def update_profile(request):
    if request.method == 'POST':
        fst_name = request.POST.get('fst_name')
        lst_name = request.POST.get('lst_name')
        selected_school_id = request.POST.get('uni')
        selected_interests = request.POST.getlist('interests')
        user = request.user
        student = Student.objects.get(user=request.user)
        user.first_name = fst_name
        user.last_name = lst_name
        student.school_id = selected_school_id
        student.interests.clear()
        for interest_id in selected_interests:
            student.interests.add(interest_id)
        user.save()
        student.save()
        messages.success(request,
                         "Profile Updated Successfully!")
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def add_review(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    student = request.user.student

    if request.method == 'POST':
        rating = request.POST.get('rating')
        description = request.POST.get('description')

        if rating and description is not None:
            review, created = Review.objects.get_or_create(
                student=student,
                document=document,
                defaults={'rating': rating, 'description': description}
            )
            if not created:
                review.rating = rating
                review.description = description
                review.save()
            messages.success(request, 'Thank you for your review!')
        else:
            messages.error(request, 'Both rating and description are required.')
    return redirect(request.META.get('HTTP_REFERER'))
