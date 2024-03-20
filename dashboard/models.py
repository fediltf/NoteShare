import hashlib
import os
import pickle

from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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

    def get_pickled_shingles(self):
        try:
            shingle = self.shingle_set.first()  # Access the related Shingle object
            if shingle:
                return shingle.pickled_shingles
        except Shingle.DoesNotExist:
            return None
    def __str__(self):
        return str(self.id)


class Shingle(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    pickled_shingles = models.TextField(blank=True, null=True)

#
# @receiver(post_save, sender=Document)
# def generate_shingles(sender, instance, created, **kwargs):
#     if created:  # Only generate shingles for newly created documents
#         text = instance.text
#         if text:
#             shingles = create_shingles(text)  # Define this function
#             shingle= ';'.join(shingles)
#             pickled_shingles = pickle.dumps(shingles)
#             # for shingle in shingles:
#             Shingle.objects.create(document=instance, shingle_text=shingle, pickled_shingles=pickled_shingles)

#
# def create_shingles(text, k=3):
#     # Tokenize the text into words
#     words = text.split()
#
#     # Create shingles by selecting consecutive sets of words
#     shingles = set()
#     for i in range(len(words) - k + 1):
#         shingle = " ".join(words[i:i + k])
#         # Hash the shingle to reduce its size
#         hashed_shingle = hashlib.sha1(shingle.encode()).hexdigest()
#         shingles.add(hashed_shingle)
#
#     return shingles