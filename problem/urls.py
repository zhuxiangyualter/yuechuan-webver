from django.urls import path
from . import views

app_name = 'problem'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:id>/', views.view, name='view'),
    path('solution/<int:id>/', views.view_solution, name='view_solution'),
    path('new/', views.new, name='new'),
    path('generate/', views.generate, name='generate'),
]