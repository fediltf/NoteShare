from django.contrib import admin

from dashboard.models import Document, Shingle, Student, Doctype, School, Topic

# Register your models here.
admin.site.register(Document)
admin.site.register(Student)
admin.site.register(Shingle)
admin.site.register(School)
admin.site.register(Doctype)
admin.site.register(Topic)
