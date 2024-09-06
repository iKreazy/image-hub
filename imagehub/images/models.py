from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone
from django.utils.timesince import timesince

from uuid import uuid4
from unidecode import unidecode
from datetime import timedelta


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

    def format_uploaded_at(self):
        return self._get_formatted_time(self.uploaded_at)

    def format_updated_at(self):
        return self._get_formatted_time(self.updated_at)

    @staticmethod
    def _get_formatted_time(dt):
        if (timezone.now() - dt) < timedelta(days=1):
            time_diff = timesince(dt).split(', ')[0].replace('\xa0', ' ')
            if time_diff.startswith('0 minutes'):
                return 'just now'
            return time_diff + " ago"
        else:
            return dt.strftime("%d.%m.%Y %H:%M")
