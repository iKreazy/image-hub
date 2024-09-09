from django.conf import settings
from django.urls import reverse
from rest_framework import serializers

from images.models import Category, Image


class CategorySelializer(serializers.ModelSerializer):
    open_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'open_url', 'name', 'slug']

    def get_open_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('image_board', kwargs={'object': obj.slug}))


class ImageSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    open_url = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['id', 'file_url', 'open_url', 'description', 'category_id', 'user_id', 'uploaded_at', 'updated_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(settings.MEDIA_URL + str(obj.file))

    def get_open_url(self, obj):
        request = self.context.get('request')
        filter_by = self.context.get('filter_by', 'category')

        if filter_by == 'account':
            slug = obj.user.username
        else:
            slug = obj.category.slug

        return request.build_absolute_uri(reverse('image_open', kwargs={
            'object': slug,
            'user_id': obj.user.id,
            'image_id': obj.id
        }))
