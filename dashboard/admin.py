from django.contrib import admin

from dashboard.models import Document, Shingle, Student

# Register your models here.
admin.site.register(Document)
admin.site.register(Student)
admin.site.register(Shingle)