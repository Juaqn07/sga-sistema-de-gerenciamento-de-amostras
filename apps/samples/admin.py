from django.contrib import admin
from .models import Cliente, Processo, Anexo, Comentario, EventoTimeline, TipoAmostra

# --- CONFIGURAÇÃO DE INLINES ---
# Permite editar registros relacionados dentro da tela do Processo


class AnexoInline(admin.TabularInline):
    """Permite adicionar/remover anexos diretamente na tela do Processo."""
    model = Anexo
    extra = 1  # Número de linhas vazias exibidas


class ComentarioInline(admin.TabularInline):
    """Visualização de comentários dentro do Processo (modo leitura/escrita)."""
    model = Comentario
    extra = 0


# --- ADMINISTRAÇÃO DOS MODELOS ---

@admin.register(Processo)
class ProcessoAdmin(admin.ModelAdmin):
    """Configuração da listagem e edição de Processos no painel Admin."""
    list_display = ('codigo', 'titulo', 'cliente',
                    'status', 'prioridade', 'criado_por')
    list_filter = ('status', 'prioridade', 'tipo_transporte')
    search_fields = ('codigo', 'titulo', 'cliente__nome')

    # Adiciona as tabelas relacionadas
    inlines = [AnexoInline, ComentarioInline]

    # Campos que não podem ser editados manualmente
    readonly_fields = ('codigo', 'data_criacao', 'ultima_atualizacao')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'responsavel', 'cidade', 'estado')
    search_fields = ('nome', 'responsavel', 'cnpj')


@admin.register(TipoAmostra)
class TipoAmostraAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem')
    # Permite reordenar rapidamente sem abrir o registro
    list_editable = ('ordem',)


# Registro simples para debug da Timeline
admin.site.register(EventoTimeline)
