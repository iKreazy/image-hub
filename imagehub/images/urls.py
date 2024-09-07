from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexImageListView.as_view(), name='index'),
    path('category', views.CategoryListView.as_view(), name='category'),
    path('recents', views.RecentsImageListView.as_view(), name='recents'),
    path('upload', views.ImageUploadView.as_view(), name='upload_image'),
    path('<slug:object>/image<int:user_id>_<int:image_id>', views.DynamicImageDetailView.as_view(), name='image_open'),
    path('<slug:object>', views.DynamicImageListView.as_view(), name='image_board')
]
