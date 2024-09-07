from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import Random

from .models import Category, Image
from .forms import ImageUploadForm


class IndexImageListView(ListView):
    model = Image
    template_name = 'images/board.html'
    context_object_name = 'images'

    def get_queryset(self):
        return Image.objects.filter(deleted_at__isnull=True).order_by(Random())[:50]


class RecentsImageListView(ListView):
    model = Image
    template_name = 'images/board.html'
    context_object_name = 'images'

    def get_queryset(self):
        return Image.objects.filter(deleted_at__isnull=True).order_by('-uploaded_at')[:10]


class DynamicImageListView(ListView):
    model = Image
    template_name = 'images/board.html'
    context_object_name = 'images'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object_ = None
        self.switch_ = None

    def dispatch(self, request, *args, **kwargs):
        self.object_ = self.kwargs.get('object')

        if Category.objects.filter(name__iexact=self.object_).exists():
            self.switch_ = 'category'
        else:
            self.switch_ = 'account'

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.switch_ == 'category':
            category = get_object_or_404(Category, slug=self.object_)
            return Image.objects.filter(category=category, deleted_at__isnull=True).order_by('-uploaded_at')[:50]

        user = get_object_or_404(get_user_model(), username=self.object_)
        return Image.objects.filter(user=user, deleted_at__isnull=True).order_by('-uploaded_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.switch_ == 'category':
            context['images'] = self.get_queryset()
            return context

        context['account'] = get_object_or_404(get_user_model(), username=self.object_)
        context['image_count'] = Image.objects.filter(user=context['account'], deleted_at__isnull=True).count()
        return context


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
        return reverse_lazy('image_open', kwargs={
            'object': image.user.username,
            'user_id': image.user.id,
            'image_id': image.id
        })


class DynamicImageDetailView(DetailView):
    model = Image
    context_object_name = 'image'
    template_name = 'images/image.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.switch_ = None

    def dispatch(self, request, *args, **kwargs):
        if Category.objects.filter(name__iexact=self.kwargs.get('object')).exists():
            self.switch_ = 'category'
        else:
            self.switch_ = 'account'

        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return get_object_or_404(Image, id=self.kwargs['image_id'], user_id=self.kwargs['user_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        image = self.get_object()

        if self.switch_ == 'category':
            next_images = Image.objects.filter(
                category=image.category,
                uploaded_at__gt=image.uploaded_at,
                deleted_at__isnull=True
            ).order_by('uploaded_at')[:10]

            if not next_images.exists():
                next_images = Image.objects.filter(
                    category=image.category,
                    deleted_at__isnull=True
                ).exclude(id=image.id).order_by('-uploaded_at')[:10]

            context['next_images'] = next_images

            category = Image.objects.filter(category=image.category, deleted_at__isnull=True)
            context['prev_image'] = category.filter(id__lt=image.id).order_by('-id').first()
            context['next_image'] = category.filter(id__gt=image.id).order_by('id').first()

            context['template_name'] = 'images/image_category.html'

        else:
            user_images = Image.objects.filter(
                user=image.user,
                uploaded_at__gt=image.uploaded_at,
                deleted_at__isnull=True
            ).order_by('-uploaded_at')[:10]

            if not user_images.exists():
                user_images = Image.objects.filter(
                    user=image.user,
                    deleted_at__isnull=True
                ).exclude(id=image.id).order_by('-uploaded_at')[:10]

            context['user_images'] = user_images

            account = Image.objects.filter(user=image.user, deleted_at__isnull=True)
            context['prev_image'] = account.filter(id__lt=image.id).order_by('-id').first()
            context['next_image'] = account.filter(id__gt=image.id).order_by('id').first()

            context['template_name'] = 'images/image_account.html'

        context['account'] = self.switch_ == 'account'
        return context
