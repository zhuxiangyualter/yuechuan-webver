from django.urls import path
from . import views

app_name = 'tag'

urlpatterns = [
    path('', views.tag, name='tag'),
]