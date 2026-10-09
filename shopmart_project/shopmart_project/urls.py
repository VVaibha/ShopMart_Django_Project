
from django.urls import path
from store.admin_reset_temp import temporary_admin_reset


from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('store.urls')),
# ]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('temporary-admin-reset/', temporary_admin_reset, name='temporary_admin_reset'),
    path('', include('store.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


