from django.urls import path
from . import views

app_name = 'AI'

urlpatterns = [
    path('gpt', views.gpt, name='gpt'),
    path('slides', views.genppt, name='slides'),
    path('slides/refresh/<int:id>', views.refresh_state, name='slides_refresh'),
]