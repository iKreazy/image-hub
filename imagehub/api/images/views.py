from rest_framework import generics
from rest_framework.exceptions import NotFound
from django.db.models.functions import Random
from django.contrib.auth import get_user_model

from images.models import Category, Image

from .serializers import CategorySelializer, ImageSerializer
from .pagination import ImagePagination


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySelializer


class RandomImageListAPIView(generics.ListAPIView):
    queryset = Image.objects.filter(deleted_at__isnull=True).order_by(Random())[:25]
    serializer_class = ImageSerializer


class RecentsImageListAPIView(generics.ListAPIView):
    queryset = Image.objects.filter(deleted_at__isnull=True).order_by('-uploaded_at')
    serializer_class = ImageSerializer
    pagination_class = ImagePagination


class CategoryImageListAPIView(generics.ListAPIView):
    serializer_class = ImageSerializer
    pagination_class = ImagePagination

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        category_id = self.kwargs.get('id')

        if slug:
            category = Category.objects.filter(slug=slug).first()
        elif category_id:
            category = Category.objects.filter(id=category_id).first()
        else:
            return Image.objects.none()

        if category:
            return Image.objects.filter(category=category, deleted_at__isnull=True).order_by('-uploaded_at')
        return Image.objects.none()


class AccountImageListAPIView(generics.ListAPIView):
    serializer_class = ImageSerializer
    pagination_class = ImagePagination

    def get_queryset(self):
        username = self.kwargs.get('username')
        user_id = self.kwargs.get('id')

        if username:
            user = get_user_model().objects.filter(username=username).first()
        elif user_id:
            user = get_user_model().objects.filter(id=user_id).first()
        else:
            return Image.objects.none()

        if user:
            return Image.objects.filter(user=user, deleted_at__isnull=True).order_by('-uploaded_at')
        return Image.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['filter_by'] = 'account'
        return context


class ImageDetailAPIView(generics.RetrieveAPIView):
    queryset = Image.objects.filter(deleted_at__isnull=True)
    serializer_class = ImageSerializer
    lookup_field = 'id'

    def get_object(self):
        image = super().get_object()
        if image is None:
            raise NotFound("Image not found")
        return image


class NextImagesAPIView(generics.ListAPIView):
    serializer_class = ImageSerializer
    pagination_class = ImagePagination

    def get_queryset(self):
        image_id = self.kwargs.get('id')
        image = Image.objects.filter(id=image_id, deleted_at__isnull=True).first()

        if not image:
            raise NotFound("Image not found")

        filter_by = self.request.query_params.get('filter_by', 'category')

        if filter_by == 'account':
            queryset = Image.objects.filter(
                user=image.user,
                uploaded_at__gt=image.uploaded_at,
                deleted_at__isnull=True
            ).order_by('uploaded_at')

            if not queryset.exists():
                queryset = (Image.objects.filter(user=image.user, deleted_at__isnull=True)
                            .exclude(id=image_id).order_by('uploaded_at'))

        else:
            queryset = Image.objects.filter(
                category=image.category,
                uploaded_at__gt=image.uploaded_at,
                deleted_at__isnull=True
            ).order_by('uploaded_at')

            if not queryset.exists():
                queryset = (Image.objects.filter(category=image.category, deleted_at__isnull=True)
                            .exclude(id=image_id).order_by('uploaded_at'))

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['filter_by'] = self.request.query_params.get('filter_by', 'category')
        return context
