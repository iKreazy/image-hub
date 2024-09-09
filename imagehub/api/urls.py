from django.urls import path

from .images.views import *

urlpatterns = [
    path('images/', RandomImageListAPIView.as_view()),
    path('images/recents', RecentsImageListAPIView.as_view()),
    path('category/list', CategoryListAPIView.as_view()),
    path('category/<slug:slug>', CategoryImageListAPIView.as_view()),
    path('category/id/<int:id>', CategoryImageListAPIView.as_view()),
    path('account/<slug:username>', AccountImageListAPIView.as_view()),
    path('account/id/<int:id>', AccountImageListAPIView.as_view()),
    path('image/id/<int:id>/', ImageDetailAPIView.as_view()),
    path('image/id/<int:id>/after', NextImagesAPIView.as_view()),
]
