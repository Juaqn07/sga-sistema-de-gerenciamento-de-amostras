from django.db import models
from django.contrib.auth.models import AbstractUser


class UsuarioCustomizado(AbstractUser):
    # Definindo as opções de Função
    FUNCAO_CHOICES = [
        ('Gestor', 'Gestor'),
        ('Vendedor', 'Vendedor'),
        ('Separador', 'Separador'),
    ]

    # Nosso campo customizado
    funcao = models.CharField(
        max_length=20, choices=FUNCAO_CHOICES, null=True, blank=True)  # type: ignore

    def __str__(self):
        return self.username
