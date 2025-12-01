from django.db import models
from django.conf import settings
from django.utils import timezone

# ==============================================================================
# 1. MODELOS AUXILIARES
# ==============================================================================


class TipoAmostra(models.Model):
    """
    Define as categorias de amostras disponíveis no sistema (ex: 'Solúvel', 'Grãos').
    A ordem define como elas aparecem nas listas de seleção.
    """
    nome = models.CharField(max_length=50, unique=True)
    ordem = models.IntegerField(
        default=0,
        help_text="Menor número aparece primeiro na lista de seleção"
    )

    class Meta:
        ordering = ['ordem', 'nome']
        verbose_name = "Tipo de Amostra"
        verbose_name_plural = "Tipos de Amostra"

    def __str__(self):
        return self.nome


class Cliente(models.Model):
    """
    Modelo de Cliente para armazenar os dados de entrega e contato.
    Centraliza as informações para reutilização em múltiplos processos.
    """
    nome = models.CharField("Nome/Razão Social", max_length=255)
    responsavel = models.CharField("A/C (Aos Cuidados de)", max_length=255)

    # --- Endereço ---
    logradouro = models.CharField(max_length=255)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField("UF", max_length=2)
    cep = models.CharField(max_length=10)

    def __str__(self):
        return self.nome


# ==============================================================================
# 2. MODELO PRINCIPAL
# ==============================================================================

# REQUISITO: Script do Banco de Dados
# A classe abaixo define a tabela, chaves primárias (id automático) e estrangeiras
class Processo(models.Model):
    """
    Representa o ciclo de vida de uma solicitação de amostra.
    Gerencia estados, responsabilidades e dados de transporte.
    """

    # --- CONSTANTES DE ESCOLHA (CHOICES) ---
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
    ]

    TRANSPORTE_CHOICES = [
        ('correios', 'Correios'),
        ('carga', 'Carga'),
        ('balcao', 'Balcão'),
    ]

    STATUS_CHOICES = [
        ('nao_atribuido', 'Não Atribuído'),
        ('atribuido', 'Atribuído'),
        ('em_separacao', 'Em Separação'),
        ('pendente', 'Pendente'),
        ('pronto_envio', 'Pronto para Envio'),
        ('em_rota', 'Em Rota de Entrega'),
        ('entregue', 'Entregue'),
        ('nao_entregue', 'Não Entregue'),
        ('cancelado', 'Cancelado'),
    ]

    # --- DADOS GERAIS ---
    # O código é gerado automaticamente no método save() (ex: PRC-2025-0001)
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    titulo = models.CharField("Título do Processo", max_length=200)
    descricao = models.TextField("Descrição")

    codigo_pedido_iniflex = models.CharField(
        "Cód. Pedido Iniflex",
        max_length=50,
        blank=True,
        null=True,
        help_text="Insira o número do pedido gerado no Iniflex para referência."
    )

    # --- CLASSIFICAÇÃO E LOGÍSTICA ---
    tipos_amostra = models.ManyToManyField(
        TipoAmostra, related_name='processos')

    tipo_transporte = models.CharField(
        max_length=50,
        choices=TRANSPORTE_CHOICES,
        default='Correios'
    )

    prioridade = models.CharField(
        max_length=20,
        choices=PRIORIDADE_CHOICES,
        default='Normal'
    )

    # REQUISITO: Chaves Estrangeiras (Foreign Key)
    # Define o relacionamento entre as tabelas Processo, Cliente e Usuário
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='processos'
    )

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='processos_criados'
    )

    responsavel_separacao = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processos_atribuidos'
    )

    # --- CONTROLE DE FLUXO ---
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='nao_atribuido'
    )

    codigo_rastreio = models.CharField(max_length=50, blank=True, null=True)

    # --- DATAS DE AUDITORIA ---
    data_criacao = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para gerar o código sequencial único.
        Formato: PRC-{ANO}-{ID_SEQUENCIAL}
        """
        if not self.codigo:
            # 1. Salva inicialmente para obter o ID do banco de dados
            super().save(*args, **kwargs)

            # 2. Gera o código formatado usando o ID recém-criado
            ano_atual = timezone.now().year
            self.codigo = f"PRC-{ano_atual}-{self.id:04d}"

            # 3. Salva novamente, forçando update para não duplicar registro
            kwargs['force_insert'] = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.titulo}"

    @property
    def is_cancelado(self):
        """Retorna True se o processo estiver cancelado."""
        return self.status == 'cancelado'

    # --- MÉTODOS DE APRESENTAÇÃO (FRONTEND) ---

    def get_status_classe_css(self):
        """Retorna a classe CSS do Bootstrap correspondente ao status atual."""
        status_map = {
            'nao_atribuido': 'bg-secondary bg-opacity-25 text-secondary',
            'atribuido': 'bg-info bg-opacity-10 text-info-emphasis',
            'em_separacao': 'bg-primary text-white',
            'pendente': 'bg-warning text-dark',
            'pronto_envio': 'bg-info text-white',
            'em_rota': 'bg-primary bg-opacity-25 text-primary-emphasis',
            'entregue': 'bg-success text-white',
            'nao_entregue': 'bg-danger text-white',
            'cancelado': 'bg-dark text-white',
        }
        return status_map.get(self.status, 'bg-secondary')

    def get_prioridade_classe_css(self):
        """Retorna a cor da badge baseada na prioridade."""
        if self.prioridade == 'alta':
            return 'bg-danger'
        if self.prioridade == 'baixa':
            return 'bg-success'
        return 'bg-secondary'  # Normal


# ==============================================================================
# 3. COMPONENTES DO PROCESSO (ANEXOS, COMENTÁRIOS, TIMELINE)
# ==============================================================================

class Anexo(models.Model):
    """Arquivos anexados ao processo (PDFs, Imagens, etc)."""
    processo = models.ForeignKey(
        Processo, on_delete=models.CASCADE, related_name='anexos')
    arquivo = models.FileField(upload_to='anexos_processos/')
    data_upload = models.DateTimeField(auto_now_add=True)

    def nome_arquivo(self):
        return self.arquivo.name.split('/')[-1]


class Comentario(models.Model):
    """
    Sistema de comentários e ocorrências internas.
    Pode ser usado para comunicação entre Vendas e Separação.
    """
    processo = models.ForeignKey(
        Processo, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.SET_NULL, null=True)
    texto = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    # Se True, este comentário funciona como um "flag" para a gestão
    encaminhar_gestao = models.BooleanField(
        "Encaminhar para Gestão", default=False)

    def __str__(self):
        return f"Comentário de {self.autor} em {self.processo}"


class EventoTimeline(models.Model):
    """
    Histórico imutável de ações (Log de auditoria visual).
    Registra mudanças de status, atribuições e edições críticas.
    """
    processo = models.ForeignKey(
        Processo, on_delete=models.CASCADE, related_name='timeline')
    titulo = models.CharField(max_length=100)  # Ex: "Status Alterado"
    # Ex: "De Pendente para Entregue"
    descricao = models.TextField(blank=True, null=True)
    data = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.SET_NULL, null=True)

    # Ícone Bootstrap para renderização (Ex: 'bi-check-lg')
    icone = models.CharField(max_length=50, default='bi-circle')

    def __str__(self):
        return f"{self.titulo} - {self.processo}"
