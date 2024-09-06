from django.shortcuts import render
from django.views.generic import ListView
from .models import Category, Image


def index(request):
    return render(request, 'main/base.html')


class CategoryListView(ListView):
    model = Category
    template_name = 'images/category.html'
    context_object_name = 'categories'

    def get_queryset(self):
        categories = Category.objects.all()
        for category in categories:
            category.latest_image = Image.objects.filter(
                category=category, deleted_at__isnull=True
            ).order_by('-uploaded_at').first()
            category.image_count = Image.objects.filter(
                category=category, deleted_at__isnull=True
            ).count()
        return categories
