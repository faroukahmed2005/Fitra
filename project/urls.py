from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('settings.urls', namespace='home')),
    path('register/', include('members.urls', namespace='members')),
    path('summernote/', include('django_summernote.urls')),
    path('i18n/',include('django.conf.urls.i18n')),
    path('api/',include('APIs.urls', namespace='apis')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'members.views.ratelimited_view'