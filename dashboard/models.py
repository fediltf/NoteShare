import base64
import hashlib
import os
import pickle
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


def user_directory_path(instance, filename):
    return f'user_{instance.user.id}/{filename}'


def filename(instance, filename):
    return filename


class Doctype(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class School(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Topic(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    points_field = models.IntegerField(default=0)
    interests = models.ManyToManyField(Topic, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}"


@receiver(post_save, sender=User)
def create_student(sender, instance, created, **kwargs):
    if created:  # Check if a new user is being created
        Student.objects.create(user=instance)

class Document(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    file_field = models.FileField(unique=True, upload_to=filename)
    info = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=100, null=False, blank=False)
    course = models.CharField(max_length=100, null=False, blank=False)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, blank=True, null=True)
    doctype = models.ForeignKey(Doctype, on_delete=models.CASCADE, blank=True, null=True)
    uni = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True)
    text = models.TextField(null=True, blank=True)
    lang = models.CharField(max_length=100, null=False, blank=False, default="en")
    keywords = models.CharField(max_length=4000, null=True, blank=True)
    cost = models.IntegerField(default=0)

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
