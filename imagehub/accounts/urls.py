from django.urls import path
from . import views

urlpatterns = [
    path('signin', views.LoginUser.as_view(), name='signin'),
    path('signup', views.RegisterUser.as_view(), name='signup'),

    path('recovery', views.RecoveryView.as_view(), name='recovery'),
    path('recovery/done', views.RecoveryDoneView.as_view(), name='recovery_done'),
    path('recovery/<uidb64>/<token>/', views.RecoveryConfirmView.as_view(), name='recovery_confirm'),
    path('recovery/complete', views.RecoveryCompleteView.as_view(), name='recovery_complete'),

    path('logout', views.UserLogout.as_view(), name='logout'),
    path('account/settings', views.UserSettings.as_view(), name='settings')
]
