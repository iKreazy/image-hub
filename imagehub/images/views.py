from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models.functions import Random

from .models import Category, Image
from .forms import ImageUploadForm, ImageEditForm


class IndexImageListView(ListView):
    model = Image
    template_name = 'images/board.html'
    context_object_name = 'images'

    def get_queryset(self):
        return Image.objects.filter(deleted_at__isnull=True).order_by(Random())[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_key'] = 'index'
        return context


class RecentsImageListView(ListView):
    model = Image
    template_name = 'images/board.html'
    context_object_name = 'images'

    def get_queryset(self):
        return Image.objects.filter(deleted_at__isnull=True).order_by('-uploaded_at')[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_key'] = 'recents'
        context['title'] = 'Recents'
        return context


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

        if Category.objects.filter(slug__iexact=self.object_).exists():
            self.switch_ = 'category'
        else:
            self.switch_ = 'account'

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.switch_ == 'category':
            category = get_object_or_404(Category, slug=self.object_)
            return Image.objects.filter(category=category, deleted_at__isnull=True).order_by('-uploaded_at')[:10]

        user = get_object_or_404(get_user_model(), username=self.object_)
        return Image.objects.filter(user=user, deleted_at__isnull=True).order_by('-uploaded_at')[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_key'] = self.switch_

        if self.switch_ == 'category':
            context['category'] = get_object_or_404(Category, slug=self.object_)
            context['images'] = self.get_queryset()
            context['title'] = context['category'].name
            return context

        context['account'] = get_object_or_404(get_user_model(), username=self.object_)
        context['image_count'] = Image.objects.filter(user=context['account'], deleted_at__isnull=True).count()
        context['title'] = ' '.join([
            context['account'].first_name,
            context['account'].last_name,
            f"(@{context['account'].username})"
        ])
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Categories'
        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Upload'
        return context


class DynamicImageDetailView(DetailView):
    model = Image
    context_object_name = 'image'
    template_name = 'images/image.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.switch_ = None

    def dispatch(self, request, *args, **kwargs):
        if Category.objects.filter(slug__iexact=self.kwargs.get('object')).exists():
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

        if image.description:
            split = image.description.split()
            context['title'] = ' '.join([*split[:3]]) + '...' if len(split) > 3 else str()
        else:
            context['title'] = ' '.join([
                image.user.first_name,
                image.user.last_name,
                f"(@{image.user.username})"
            ])

        context['page_key'] = self.switch_
        context['category'] = image.category
        context['account'] = image.user if self.switch_ == 'account' else False
        return context


class ImageEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Image
    form_class = ImageEditForm
    template_name = 'images/upload.html'
    success_url = reverse_lazy('image_list')

    def get_object(self, queryset=None):
        return get_object_or_404(Image, id=self.kwargs['image_id'], user__id=self.kwargs['user_id'])

    def test_func(self):
        return self.request.user == self.get_object().user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        context['image'] = self.get_object()
        context['title'] = 'Edit'
        return context

    def get_success_url(self):
        image = self.get_object()
        return reverse_lazy('image_open', kwargs={
            'object': image.user.username,
            'user_id': image.user.id,
            'image_id': image.id
        })


class ImageDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        image = get_object_or_404(Image, id=self.kwargs['image_id'])
        return self.request.user == image.user

    def post(self, request, *args, **kwargs):
        image = get_object_or_404(Image, id=self.kwargs['image_id'])
        image.deleted_at = timezone.now()
        image.save()
        return redirect(reverse('image_board', kwargs={'object': image.user.username}))
