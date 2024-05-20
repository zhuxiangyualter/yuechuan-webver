from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('login/', views.login_, name='login'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('cloud/', views.cloud, name='cloud'),
    path('profile/edit', views.edit_profile, name='editProfile'),
]