import os
import pdfplumber
from django import template
from django.conf import settings
from dashboard.models import Document
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO

register = template.Library()


@register.filter
def basename(document_id):
    # return os.path.basename(path)
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
def restricted_pdf(document_id):
    document = Document.objects.filter(id=document_id).first()
    if document:
        name = document.file_field.name
        p_name = os.path.splitext(name)[0]
        return f'/media/{p_name}_restricted.pdf'
