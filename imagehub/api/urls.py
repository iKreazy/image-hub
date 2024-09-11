from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

from .accounts.views import *
from .images.views import *

urlpatterns = [
    path('images', RandomImageListAPIView.as_view()),
    path('images/recents', RecentsImageListAPIView.as_view()),
    path('images/category/<slug:slug>', CategoryImageListAPIView.as_view()),
    path('images/category/id/<int:id>', CategoryImageListAPIView.as_view()),
    path('images/account/<slug:username>', AccountImageListAPIView.as_view()),
    path('images/account/id/<int:id>', AccountImageListAPIView.as_view()),

    path('category/create', CreateCategoryView.as_view(), name='api-category-create'),
    path('category/list', CategoryListAPIView.as_view()),
    path('category/id/<int:id>/edit', UpdateCategoryView.as_view()),
    path('category/id/<int:id>/delete', DeleteCategoryView.as_view()),

    path('account/signup', AccountSignUpView.as_view(), name='api-account-signup'),
    path('account/info', AccountInfoView.as_view()),
    path('account/settings', AccountSettingsView.as_view(), name='api-account-settings'),
    path('account/delete', AccountDeleteView.as_view()),

    path('image/upload', UploadImageView.as_view(), name='api-image-upload'),
    path('image/id/<int:id>', ImageDetailAPIView.as_view()),
    path('image/id/<int:id>/after', NextImagesAPIView.as_view()),
    path('image/id/<int:id>/edit', UpdateImageView.as_view()),
    path('image/id/<int:id>/delete', DeleteImageView.as_view()),

    path('token', TokenObtainPairView.as_view(), name='api-token'),
    path('token/refresh', TokenRefreshView.as_view()),
    path('token/logout', TokenBlacklistView.as_view()),

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
