import base64
import hashlib
import os
import pickle
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User



def user_directory_path(instance, filename):
    return f'user_{instance.user.id}/{filename}'


def filename(instance, filename):
    return filename




class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_field = models.FileField(unique=True, upload_to=filename)
    info = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=100, null=False, blank=False)
    course = models.CharField(max_length=100, null=False, blank=False)
    subject = models.CharField(max_length=100, null=False, blank=False)
    doctype = models.CharField(max_length=100, null=False, blank=False)
    uni = models.CharField(max_length=100, null=False, blank=False)
    text = models.TextField(null=True, blank=True)
    lang = models.CharField(max_length=100, null=False, blank=False, default="en")
    keywords = models.CharField(max_length=4000, null=True, blank=True)

    def get_pickled_shingles(self):
        try:
            shingle = self.shingle_set.first()  # Access the related Shingle object
            if shingle:
                # return shingle.pickled_shingles
                return base64.b64decode(shingle.pickled_shingles)
        except Shingle.DoesNotExist:
            return None
    def __str__(self):
        return str(self.id)


class Shingle(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    pickled_shingles = models.TextField(blank=True, null=True)