from django.urls import path
from . import views  # Importa as views do app

# Isso é essencial para o Django saber que 'accounts:login' pertence a este app
app_name = 'accounts'

urlpatterns = [
    # URL: / (raiz)
    path('', views.login_view, name='login'),

    # URL: /cadastrar-usuario/
    path('cadastrar-usuario/', views.register_user_view, name='cadastrar_usuario'),

    # URL: /perfil/
    path('perfil/', views.profile_view, name='perfil'),

    # URL: /recuperar-senha/
    path('recuperar-senha/', views.password_recovery_view, name='recuperar_senha'),

    # URL: /logout/ (Esta não precisa de template, só de uma view)
    path('logout/', views.logout_view, name='logout'),
]
