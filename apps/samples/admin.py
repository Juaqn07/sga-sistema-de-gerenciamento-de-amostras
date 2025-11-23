from django.contrib import admin
from .models import Cliente, Processo, Anexo, Comentario, EventoTimeline

# Configuração para editar Anexos dentro da tela do Processo


class AnexoInline(admin.TabularInline):
    model = Anexo
    extra = 1


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0


@admin.register(Processo)
class ProcessoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'titulo', 'cliente',
                    'status', 'prioridade', 'criado_por')
    list_filter = ('status', 'prioridade', 'tipo_transporte')
    search_fields = ('codigo', 'titulo', 'cliente__nome')
    inlines = [AnexoInline, ComentarioInline]
    readonly_fields = ('codigo', 'data_criacao', 'ultima_atualizacao')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'responsavel', 'cidade', 'estado')
    search_fields = ('nome', 'responsavel')


admin.site.register(EventoTimeline)
