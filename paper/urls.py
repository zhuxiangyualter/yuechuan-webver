from django.urls import path
from . import views

app_name = 'paper'

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new, name='new'),
    path('<int:id>/', views.view, name='view'),
    path('<int:id>/statistics/', views.statistics, name='statistics'),
    path('<int:id>/submission/', views.paper_submission, name='papersubmissions'),
    path('submission/', views.submissions, name='submissions'),
    path('submission/<int:id>/', views.submission, name='submission'),
    path('submission/<int:id>/judge/', views.judge, name='judge'),
]