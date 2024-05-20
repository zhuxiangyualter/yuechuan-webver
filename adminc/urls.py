from django.urls import path
from . import views

app_name = 'adminc'

urlpatterns = [
    path('user/', views.user, name='user'),
    path('student/', views.student, name='student'),
    path('facility/', views.facility, name='facility')
]