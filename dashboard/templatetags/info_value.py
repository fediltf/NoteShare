import os
from datetime import datetime

import pdfplumber
from dateutil.relativedelta import relativedelta
from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.timesince import timesince
from dashboard.models import Document, Student, Review

register = template.Library()


@register.filter
def basename(document_id):
    file_info = Document.objects.filter(id=document_id)
    if file_info.exists():
        return file_info.first().file_field.name


@register.filter
def desc_value(document_id):
    file_info = Document.objects.filter(id=document_id)
    if file_info.exists():
        return file_info.first().info
    else:
        return ""


@register.filter
def title_value(document_id):
    file_info = Document.objects.filter(id=document_id)
    if file_info.exists():
        return file_info.first().title
    else:
        return ""


@register.filter
def course_value(document_id):
    file_info = Document.objects.filter(id=document_id)
    if file_info.exists():
        return file_info.first().course.id
    else:
        return ""


@register.filter
def restricted_pdf(document_id):
    document = Document.objects.filter(id=document_id).first()
    if document:
        name = document.file_field.name
        p_name = os.path.splitext(name)[0]
        return f'/media/{p_name}_restricted.pdf'


@register.filter
def doctype_value(document_id):
    file_info = Document.objects.filter(id=document_id)
    if file_info.exists():
        return file_info.first().doctype.id
    else:
        return ""


@register.filter
def uni_value(document_id):
    file_info = Document.objects.filter(id=document_id)
    if file_info.exists():
        return file_info.first().uni.id
    else:
        return ""


@register.filter
def display_value(document_id):
    file_info = Document.objects.filter(id=document_id)
    if file_info.exists():

        if file_info.first().title != "":
            return file_info.first().title
        return file_info.first().file_field.name
    else:
        return ""


@register.filter
def file_img(document_id):
    # return os.path.basename(path)
    file_info = Document.objects.filter(id=document_id)
    if file_info.exists():
        name = file_info.first().file_field.name
        fp = os.path.join(settings.MEDIA_ROOT, name)
        with pdfplumber.open(fp) as pdf:
            first_page = pdf.pages[0]
            images = first_page.images
        return images


@register.filter
def nb_pages(document_id):
    file_info = Document.objects.filter(id=document_id)
    if file_info.exists():
        name = file_info.first().file_field.name
        fp = os.path.join(settings.MEDIA_ROOT, name)
        with pdfplumber.open(fp) as pdf:
            nb = len(pdf.pages)
        if nb < 10:
            return '0' + str(nb)
        return str(nb)
    return '00'

@register.filter
def nb_pages_int(document_id):
    file_info = Document.objects.filter(id=document_id)
    if file_info.exists():
        name = file_info.first().file_field.name
        fp = os.path.join(settings.MEDIA_ROOT, name)
        with pdfplumber.open(fp) as pdf:
            nb = len(pdf.pages)
        return (nb)


@register.filter
def restricted_pdf(document_id):
    document = Document.objects.filter(id=document_id).first()
    if document:
        name = document.file_field.name
        p_name = os.path.splitext(name)[0]
        return f'/media/{p_name}_restricted.pdf'


@register.filter
def doc_path(document_id):
    document = Document.objects.filter(id=document_id).first()
    if document:
        name = document.file_field.name
        return f'/media/{name}'


@register.filter
def student_review(student_id, document_id):
    document = Document.objects.filter(id=document_id).first()
    student = Student.objects.get(id=student_id)
    try:
        review = Review.objects.get(student=student, document=document)
        return review
    except ObjectDoesNotExist:
        return None


@register.filter
def document_reviews(document_id):
    document = Document.objects.filter(id=document_id).first()
    if document:
        return Review.objects.filter(document=document)
    else:
        return []


@register.filter
def timesince_custom(value):
    return timesince(value)


@register.filter
def days_ago(value):
    now = timezone.now()
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.get_current_timezone())
    if timezone.is_naive(now):
        now = timezone.make_aware(now, timezone.get_current_timezone())
    delta = relativedelta(now, value)
    if delta.years > 0:
        return f"{delta.years} year{'s' if delta.years > 1 else ''} ago"
    elif delta.months > 0:
        return f"{delta.months} month{'s' if delta.months > 1 else ''} ago"
    elif delta.days > 0:
        return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
    elif delta.hours > 0:
        return f"{delta.hours} hour{'s' if delta.hours > 1 else ''} ago"
    else:
        return "just now"
