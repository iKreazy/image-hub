from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.urls import reverse
from django.utils.html import format_html

from .models import Category, Image


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug_link', 'created_at')
    search_fields = ('name', 'slug')

    @admin.display(description="Slug")
    def slug_link(self, obj):
        url = reverse('image_board', kwargs={'object': obj.slug})
        return format_html('<a href="{}" target="_blank">{}</a>', url, obj.slug)


class DeletedFilter(SimpleListFilter):
    title = 'deleted'
    parameter_name = 'deleted_status'

    def lookups(self, request, model_admin):
        return (
            ('deleted', 'Deleted'),
            ('not_deleted', 'Not Deleted'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'deleted':
            return queryset.exclude(deleted_at__isnull=True)
        if self.value() == 'not_deleted':
            return queryset.filter(deleted_at__isnull=True)
        return queryset


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'thumbnail', 'description', 'user_link', 'category', 'uploaded_at', 'delete_status', 'deleted_at')
    list_filter = ('category', DeletedFilter)
    search_fields = ('description',)
    exclude = ('delete',)

    @admin.display(description="User")
    def user_link(self, obj):
        url = reverse('image_board', kwargs={'object': obj.user.username})
        return format_html('<a href="{}" target="_blank">{}</a>', url, obj.user.username)

    @admin.display(description="Image")
    def thumbnail(self, obj):
        if obj.file:
            url = reverse('image_open', kwargs={
                'object': obj.user.username,
                'user_id': obj.user.id,
                'image_id': obj.id
            })
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="width: 100px; height: auto;"/></a>',
                url, obj.file.url)
        return ''

    @admin.display(description="Delete")
    def delete_status(self, obj):
        if obj.deleted_at:
            return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')
        else:
            return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')
