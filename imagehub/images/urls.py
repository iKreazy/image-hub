from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('category', views.CategoryListView.as_view(), name='category'),
    path('upload', views.ImageUploadView.as_view(), name='upload_image'),
    path('<str:username>/image<int:user_id>_<int:image_id>', views.ImageAccountDetailView.as_view(), name='image_account'),
    path('<slug:category>/image<int:user_id>_<int:image_id>', views.ImageCategoryDetailView.as_view(), name='image_category'),
]
