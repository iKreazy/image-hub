from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models.functions import Random
from django.contrib.auth import get_user_model
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from images.models import Category, Image

from .serializers import CategorySerializer, ImageSerializer
from .pagination import ImagePagination


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = []


class RandomImageListAPIView(generics.ListAPIView):
    queryset = Image.objects.filter(deleted_at__isnull=True).order_by(Random())[:25]
    serializer_class = ImageSerializer
    permission_classes = []


class RecentsImageListAPIView(generics.ListAPIView):
    queryset = Image.objects.filter(deleted_at__isnull=True).order_by('-uploaded_at')
    serializer_class = ImageSerializer
    permission_classes = []
    pagination_class = ImagePagination


class CategoryImageListAPIView(generics.ListAPIView):
    serializer_class = ImageSerializer
    permission_classes = []
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
    permission_classes = []
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
    permission_classes = []
    lookup_field = 'id'

    def get_object(self):
        image = super().get_object()
        if image is None:
            raise NotFound("Image not found")
        return image


class NextImagesAPIView(generics.ListAPIView):
    serializer_class = ImageSerializer
    permission_classes = []
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


class UploadImageView(generics.CreateAPIView):
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateImageView(generics.UpdateAPIView):
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            image = Image.objects.get(pk=self.kwargs.get('id'))
        except Image.DoesNotExist:
            raise NotFound("Image not found")

        if image.deleted_at is not None:
            raise NotFound("Image not found")

        return image

    @extend_schema(exclude=True)
    def put(self, request, *args, **kwargs):
        return Response({"detail": "Method 'PUT' not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        image = self.get_object()
        if image.user != request.user:
            return Response({"detail": "You do not have permission to edit this image."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(image, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteImageView(generics.GenericAPIView):
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            image = Image.objects.get(pk=self.kwargs.get('id'))
        except Image.DoesNotExist:
            raise NotFound("Image not found")

        if image.deleted_at is not None:
            raise NotFound("Image not found")

        return image

    def delete(self, request, *args, **kwargs):
        image = self.get_object()

        if image.user != request.user:
            return Response({"detail": "You do not have permission to delete this image."},
                            status=status.HTTP_403_FORBIDDEN)

        image.deleted_at = timezone.now()
        image.save()

        return Response({"detail": "Image marked as deleted."}, status=status.HTTP_200_OK)


class CreateCategoryView(generics.CreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateCategoryView(generics.UpdateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self):
        try:
            return Category.objects.get(pk=self.kwargs.get('id'))
        except Category.DoesNotExist:
            raise NotFound("Category not found")

    @extend_schema(exclude=True)
    def put(self, request, *args, **kwargs):
        return Response({"detail": "Method 'PUT' not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        category = self.get_object()
        serializer = self.get_serializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteCategoryView(generics.DestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self):
        try:
            return Category.objects.get(pk=self.kwargs.get('id'))
        except Category.DoesNotExist:
            raise NotFound("Category not found")

    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        category.delete()
        return Response({"detail": "Category deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
