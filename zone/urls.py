from django.urls import path
from . import views

app_name = 'zone'

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new, name='new'),
    path('<int:id>/', views.view, name='view'),
]