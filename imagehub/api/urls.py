from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

from .accounts.views import *
from .images.views import *

urlpatterns = [
    path('images', RandomImageListAPIView.as_view()),
    path('images/recents', RecentsImageListAPIView.as_view()),

    path('category/create', CreateCategoryView.as_view()),
    path('category/list', CategoryListAPIView.as_view()),
    path('category/<slug:slug>', CategoryImageListAPIView.as_view()),
    path('category/id/<int:id>', CategoryImageListAPIView.as_view()),
    path('category/id/<int:id>/edit', UpdateCategoryView.as_view()),
    path('category/id/<int:id>/delete', DeleteCategoryView.as_view()),

    path('account/signup', AccountSignUpView.as_view()),
    path('account/info', AccountInfoView.as_view()),
    path('account/settings', AccountSettingsView.as_view()),
    path('account/delete', AccountDeleteView.as_view()),
    path('account/<slug:username>', AccountImageListAPIView.as_view()),
    path('account/id/<int:id>', AccountImageListAPIView.as_view()),

    path('image/upload', UploadImageView.as_view()),
    path('image/id/<int:id>', ImageDetailAPIView.as_view()),
    path('image/id/<int:id>/after', NextImagesAPIView.as_view()),
    path('image/id/<int:id>/edit', UpdateImageView.as_view()),
    path('image/id/<int:id>/delete', DeleteImageView.as_view()),

    path('token', TokenObtainPairView.as_view()),
    path('token/refresh', TokenRefreshView.as_view()),
    path('token/logout', TokenBlacklistView.as_view()),
]
