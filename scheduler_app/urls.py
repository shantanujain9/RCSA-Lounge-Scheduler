from django.urls import path
from . import views
from .views import generate_schedule


urlpatterns = [
    path('', views.index, name='index'),
    path('generate_schedule/', generate_schedule, name='generate_schedule'),
    path('upload_files/', views.upload_files, name='upload_files'),
]
