from django.urls import path
from . import views

urlpatterns = [
    path('signin', views.LoginUser.as_view(), name='signin'),
    path('signup', views.LoginUser.as_view(), name='signup'),
    path('logout', views.UserLogout.as_view(), name='logout')
]
