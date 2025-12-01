from django.core.management.base import BaseCommand
from apps.samples.models import Processo
from apps.correios.logic import update_process_tracking


class Command(BaseCommand):
    """
    Comando de gerenciamento (Django Management Command) para atualização em massa
    dos rastreios dos Correios.

    Uso: python manage.py update_tracking
    Geralmente configurado para rodar via CRON ou Celery Beat periodicamente.
    """
    help = 'Atualiza o rastreamento de todos os processos ativos via API Correios'

    def handle(self, *args, **kwargs):
        """
        Método principal executado ao chamar o comando.
        Seleciona processos elegíveis e invoca a lógica de atualização para cada um.
        """
        self.stdout.write("Iniciando atualização massiva de rastreios...")

        # --- FILTRAGEM DE PROCESSOS ---
        # Seleciona apenas processos que:
        # 1. Utilizam Correios como transporte.
        # 2. NÃO estão em status finalizados (entregue, cancelado, etc).
        # 3. Possuem código de rastreio preenchido.
        eligible_processes = Processo.objects.filter(
            tipo_transporte='correios'
        ).exclude(
            status__in=['entregue', 'cancelado', 'nao_entregue']
        ).exclude(
            codigo_rastreio__isnull=True
        ).exclude(
            codigo_rastreio=''
        )

        total_processes = eligible_processes.count()
        updated_count = 0

        # Itera sobre cada processo elegível
        for process in eligible_processes:
            try:
                self.stdout.write(
                    f"Verificando {process.codigo} ({process.codigo_rastreio})...")

                # Chama a lógica centralizada (mesma usada na View)
                was_updated = update_process_tracking(process)

                if was_updated:
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"-> {process.codigo} ATUALIZADO!"))

            except Exception as error:
                # Em caso de erro num processo específico, loga e continua para o próximo
                self.stdout.write(self.style.ERROR(
                    f"-> Erro em {process.codigo}: {error}"))

        # Resumo final da operação
        self.stdout.write(self.style.SUCCESS(
            f"FIM. Processados: {total_processes}. Atualizados: {updated_count}."
        ))
