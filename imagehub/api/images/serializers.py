from django.conf import settings
from django.urls import reverse
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

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
    file = serializers.ImageField()
    file_url = serializers.SerializerMethodField()
    open_url = serializers.SerializerMethodField()
    category_id = serializers.IntegerField()

    class Meta:
        model = Image
        fields = [
            'id', 'file', 'file_url', 'open_url', 'description',
            'category_id', 'user_id', 'uploaded_at', 'updated_at']
        read_only_fields = ['user', 'uploaded_at', 'updated_at', 'deleted_at']

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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('category', None)
        representation.pop('file', None)
        return representation

    def validate(self, data):
        if self.instance is None:
            if not data.get('file'):
                raise serializers.ValidationError({'file': 'This field is required.'})
            if not data.get('category_id'):
                raise serializers.ValidationError({'category_id': 'This field is required.'})

        print('x', data)
        category_id = data.get('category_id')
        if category_id:
            data['category'] = get_object_or_404(Category, id=category_id)

        return data

    def update(self, instance, data):
        instance.description = data.get('description', instance.description)
        instance.category = data.get('category', instance.category)
        instance.save()
        return instance
