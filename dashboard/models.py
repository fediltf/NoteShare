import base64
import hashlib
import os
import pickle
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator


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
    coef = models.DecimalField(max_digits=2, decimal_places=1,
                               validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], null=True, blank=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    points_field = models.IntegerField(default=0)
    interests = models.ManyToManyField(Topic)
    school = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True)
    purchased_documents = models.ManyToManyField('Document', related_name='purchasers', blank=True)

    def __str__(self):
        return f"{self.user.username}"


@receiver(post_save, sender=User)
def create_student(sender, instance, created, **kwargs):
    if created:  # Check if a new user is being created
        Student.objects.create(user=instance)


class Document(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='uploaded_documents')
    upload_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    file_field = models.FileField(unique=True, upload_to=filename)
    info = models.TextField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=100, null=False, blank=False)
    course = models.ForeignKey(Topic, on_delete=models.CASCADE, blank=True, null=True)
    doctype = models.ForeignKey(Doctype, on_delete=models.CASCADE, blank=True, null=True)
    uni = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True)
    text = models.TextField(null=True, blank=True)
    lang = models.CharField(max_length=100, null=False, blank=False, default="en")
    keywords = models.CharField(max_length=4000, null=True, blank=True)
    cost = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)

    def calculate_average_rating(self):
        average = self.reviews.aggregate(Avg('rating'))['rating__avg']
        self.average_rating = average if average is not None else 0
        self.save()

    def get_pickled_shingles(self):
        try:
            shingle = self.shingle_set.first()  # Access the related Shingle object
            if shingle:
                return base64.b64decode(shingle.pickled_shingles)
        except Shingle.DoesNotExist:
            return None

    def __str__(self):
        return str(self.title)

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('upload', 'Upload'),
        ('purchase', 'Purchase'),
    ]

    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    transaction_date = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.user.username} - {self.transaction_type} - {self.document.title}"

class Review(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'document')

    def __str__(self):
        return f'{self.student.user.username} - {self.document.id} - {self.rating}'


@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_document_rating(sender, instance, **kwargs):
    document = instance.document
    document.calculate_average_rating()


class Shingle(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    pickled_shingles = models.TextField(blank=True, null=True)
