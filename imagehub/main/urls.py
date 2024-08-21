from django.urls import path, include

urlpatterns = [
    path('', include('images.urls'))
]
