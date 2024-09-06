from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from uuid import uuid4
from unidecode import unidecode


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def slug(self):
        return slugify(unidecode(self.name))


def get_images_uuid(instance, filename):
    ext = filename.split('.')[-1]
    return f'images/{uuid4().hex}.{ext}'


class Image(models.Model):
    file = models.ImageField(upload_to=get_images_uuid)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    delete = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.description[:30]}"
