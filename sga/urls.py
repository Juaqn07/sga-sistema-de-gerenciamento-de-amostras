from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Delega URLs do app 'dashboard'
    path('dashboard/', include('apps.dashboard.urls')),

    # 2. Delega URLs do app 'samples' (processos)
    path('processos/', include('apps.samples.urls')),

    # 3. Delega URLs do app 'accounts' (login, perfil, etc.)
    path('', include('apps.accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)  # type: ignore
