from django.db import models
from django.contrib.auth.models import AbstractUser


class UsuarioCustomizado(AbstractUser):
    # Definindo as opções de Função
    FUNCAO_CHOICES = [
        ('Gestor', 'Gestor'),
        ('Vendedor', 'Vendedor'),
        ('Separador', 'Separador'),
    ]

    funcao = models.CharField(
        max_length=20, choices=FUNCAO_CHOICES, null=True, blank=True)  # type: ignore

    setor = models.CharField(max_length=50, null=True,
                             blank=True)  # type: ignore

    # 'fotos_perfil/' é a pasta para onde as fotos irão
    foto = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)

    def __str__(self):
        return self.username
