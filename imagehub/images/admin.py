from django.contrib import admin
from .models import Category, Image


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'category', 'uploaded_at', 'delete')
    list_filter = ('category', 'delete')
    search_fields = ('description',)
