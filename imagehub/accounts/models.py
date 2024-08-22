from django.contrib.auth.models import AbstractUser
from django.db import models
from uuid import uuid4


def get_avatar_uuid(instance, filename):
    ext = filename.split('.')[-1]
    return f'avatars/{uuid4().hex}.{ext}'


class AccountModel(AbstractUser):
    avatar = models.ImageField(upload_to=get_avatar_uuid, blank=True, null=True, verbose_name='avatar')

    def __str__(self):
        return self.username
