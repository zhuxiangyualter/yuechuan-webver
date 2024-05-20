from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('native-admin/', admin.site.urls),
    path('', include('index.urls')),
    path('user/', include('user.urls')),
    path('problem/', include('problem.urls')),
    path('zone/', include('zone.urls')),
    path('chat/', include('chat.urls')),
    path('ai/', include('AI.urls')),
    path('tag/', include('tag.urls')),
    path('paper/', include('paper.urls')),
    path('admin/', include('adminc.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
