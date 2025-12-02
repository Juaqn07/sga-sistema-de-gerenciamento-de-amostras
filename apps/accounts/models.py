from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.core.validators import validar_tamanho_arquivo


class UsuarioCustomizado(AbstractUser):
    """
    Modelo de Usuário estendido (substitui o User padrão do Django).
    Adiciona campos específicos para a regra de negócio da empresa (Função e Setor).
    """

    # Opções de função para controle de permissões no frontend/backend
    FUNCAO_CHOICES = [
        ('Gestor', 'Gestor'),
        ('Vendedor', 'Vendedor'),
        ('Separador', 'Separador'),
    ]

    # Campos Personalizados
    funcao = models.CharField(
        max_length=20,
        choices=FUNCAO_CHOICES,
        null=True,
        blank=True,
        help_text="Define o nível de acesso do usuário no sistema."
    )

    setor = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    # Armazenamento de mídia: 'fotos_perfil/' será criado dentro da pasta MEDIA_ROOT
    foto = models.ImageField(
        upload_to='fotos_perfil/',
        null=True,
        blank=True,
        validators=[validar_tamanho_arquivo]
    )

    def __str__(self):
        """Retorna o username como representação textual do objeto."""
        return self.username
