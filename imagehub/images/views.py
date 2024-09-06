from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Category, Image
from .forms import ImageUploadForm


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


class ImageUploadView(LoginRequiredMixin, CreateView):
    model = Image
    form_class = ImageUploadForm
    template_name = 'images/upload.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        image = self.object
        return reverse_lazy('image_account', kwargs={
            'username': image.user.username,
            'user_id': image.user.id,
            'image_id': image.id
        })


class ImageAccountDetailView(DetailView):
    model = Image
    context_object_name = 'image'
    template_name = 'images/image.html'
    extra_context = {'template_name': 'images/image_account.html'}

    def get_object(self):
        return get_object_or_404(Image, id=self.kwargs['image_id'], user_id=self.kwargs['user_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        image = self.get_object()
        user_images = Image.objects.filter(user_id=image.user_id).exclude(id=image.id).order_by('-uploaded_at')[:10]
        context['user_images'] = user_images
        return context


class ImageCategoryDetailView(DetailView):
    model = Image
    context_object_name = 'image'
    template_name = 'images/image.html'
    extra_context = {'template_name': 'images/image_category.html'}

    def get_object(self):
        return get_object_or_404(Image, id=self.kwargs['image_id'], user_id=self.kwargs['user_id'])
