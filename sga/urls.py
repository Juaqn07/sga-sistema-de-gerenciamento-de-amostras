from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Delega URLs do app 'dashboard'
    path('dashboard/', include('apps.dashboard.urls')),

    # 2. Delega URLs do app 'samples' (processos)
    path('processos/', include('apps.samples.urls')),

    # 3. Delega URLs do app 'accounts' (login, perfil, etc.)
    path('', include('apps.accounts.urls')),
]
