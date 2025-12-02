import os
from django.core.exceptions import ValidationError


def validar_tamanho_arquivo(file):
    """
    Impede upload de arquivos maiores que 10MB.
    """
    limite_mb = 10
    if file.size > limite_mb * 1024 * 1024:
        raise ValidationError(
            f"O arquivo é muito grande. O tamanho máximo é {limite_mb}MB.")


def validar_extensao_segura(file):
    """
    Permite apenas arquivos de documentos seguros e imagens.
    """
    ext = os.path.splitext(file.name)[1].lower()
    extensoes_validas = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']

    if ext not in extensoes_validas:
        raise ValidationError(
            f"Extensão não suportada. Use: {', '.join(extensoes_validas)}")
