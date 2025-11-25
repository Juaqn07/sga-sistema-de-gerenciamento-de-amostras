from django.db import models
from django.conf import settings
from django.utils import timezone

# 1. Modelo para Múltiplos Tipos de Amostras


class TipoAmostra(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    ordem = models.IntegerField(
        default=0, help_text="Menor número aparece primeiro")

    class Meta:
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome

# 2. Modelo de Cliente (Para armazenar os dados de entrega)


class Cliente(models.Model):
    nome = models.CharField("Nome/Razão Social", max_length=255)
    responsavel = models.CharField("A/C (Aos Cuidados de)", max_length=255)

    # Endereço
    logradouro = models.CharField(max_length=255)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField("UF", max_length=2)
    cep = models.CharField(max_length=10)

    def __str__(self):
        return self.nome

# 3. Modelo Principal: Processo


class Processo(models.Model):
    # Opções (Choices) para os campos de seleção
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

    # Status do Fluxo (Baseado no seu modal de processos-do-setor.html)
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

    # Campos do Processo
    # O código será gerado automaticamente (ex: PRC-2025-0001)
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

    tipos_amostra = models.ManyToManyField(
        TipoAmostra, related_name='processos')
    tipo_transporte = models.CharField(
        max_length=50, choices=TRANSPORTE_CHOICES, default='Correios')
    prioridade = models.CharField(
        max_length=20, choices=PRIORIDADE_CHOICES, default='Normal')

    # Relacionamentos
    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, related_name='processos')
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='processos_criados')
    responsavel_separacao = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processos_atribuidos'
    )

    # Controle de Fluxo
    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default='nao_atribuido')
    codigo_rastreio = models.CharField(max_length=50, blank=True, null=True)

    # Datas
    data_criacao = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Lógica para gerar o código único (PRC-ANO-ID)
        if not self.codigo:
            # Salva primeiro para ter um ID
            super().save(*args, **kwargs)
            ano = timezone.now().year
            # Gera o código: PRC-2025-0001 (preenchido com zeros à esquerda)
            self.codigo = f"PRC-{ano}-{self.id:04d}"
            # Salva novamente com o código
            kwargs['force_insert'] = False  # Evita erro de insert duplicado
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.titulo}"

    @property
    def is_cancelado(self):
        return self.status == 'cancelado'

    # Métodos auxiliares para o template (Bootstrap classes)
    def get_status_classe_css(self):
        if self.status == 'em_separacao':
            return 'bg-primary-subtle text-primary'
        if self.status == 'pendente':
            return 'bg-warning-subtle text-warning'
        if self.status == 'entregue':
            return 'bg-success-subtle text-success'
        if self.status == 'nao_entregue':
            return 'bg-danger-subtle text-danger'
        if self.status == 'cancelado':
            return 'bg-dark text-white'
        return 'bg-secondary-subtle text-secondary'

    def get_prioridade_classe_css(self):
        if self.prioridade == 'alta':
            return 'bg-danger'
        if self.prioridade == 'baixa':
            return 'bg-success'
        return 'bg-secondary'  # Normal

# 4. Anexos (Arquivos)


class Anexo(models.Model):
    processo = models.ForeignKey(
        Processo, on_delete=models.CASCADE, related_name='anexos')
    arquivo = models.FileField(upload_to='anexos_processos/')
    data_upload = models.DateTimeField(auto_now_add=True)

    def nome_arquivo(self):
        return self.arquivo.name.split('/')[-1]

# 5. Comentários e Ocorrências


class Comentario(models.Model):
    processo = models.ForeignKey(
        Processo, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.SET_NULL,
                              null=True)
    texto = models.TextField()
    data = models.DateTimeField(auto_now_add=True)
    # Se marcado como True, pode disparar um alerta para o Gestor
    encaminhar_gestao = models.BooleanField(
        "Encaminhar para Gestão", default=False)

    def __str__(self):
        return f"Comentário de {self.autor} em {self.processo}"

# 6. Timeline (Histórico de Ações)


class EventoTimeline(models.Model):
    processo = models.ForeignKey(
        Processo, on_delete=models.CASCADE, related_name='timeline')
    # Ex: "Status Alterado", "Anexo Adicionado"
    titulo = models.CharField(max_length=100)
    # Ex: "Mudou de Pendente para Em Separação"
    descricao = models.TextField(blank=True, null=True)
    data = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.SET_NULL, null=True)

    # Ícone para o template (Ex: 'bi-check-lg', 'bi-truck')
    icone = models.CharField(max_length=50, default='bi-circle')

    def __str__(self):
        return f"{self.titulo} - {self.processo}"
