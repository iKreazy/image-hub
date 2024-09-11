from django import template

from images.models import Category, Image

register = template.Library()


@register.simple_tag(takes_context=True)
def get_categories(context):
    categories = Category.objects.all()

    current = None
    for category in categories:
        if f'/{category.slug}' in context['request'].path:
            current = category
            break

    return {'categories': categories, 'current': current}


@register.simple_tag
def user_image_count(user):
    return Image.objects.filter(user=user, deleted_at__isnull=True).count()


@register.filter
def truncate_words(value, max_words=32):
    words = value.split()
    if len(words) > max_words:
        return ' '.join(words[:max_words]) + '...'
    return value
