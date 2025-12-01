from apps.samples.models import Processo, EventoTimeline
from .services import CorreiosService


def update_process_tracking(processo):
    """
    Função principal (CORE) para atualização de rastreamento de um processo.

    O fluxo de execução é:
    1. Consulta API dos Correios (track_object).
    2. Compara eventos recebidos com a Timeline existente no banco (SGA).
    3. Atualiza o Status do Processo se houver entrega ou devolução.
    4. Retorna um booleano indicando se houve alterações.

    Args:
        processo: Instância do modelo Processo que será atualizada.

    Returns:
        True se novos eventos foram adicionados ou o status mudou, False caso contrário.
    """

    # Validação inicial: se não tem código, não há o que rastrear
    if not processo.codigo_rastreio:
        return False

    # Instancia o serviço e consulta a API
    service = CorreiosService()
    tracking_data = service.track_object(processo.codigo_rastreio)

    # Verifica se houve retorno válido e se há eventos na resposta
    if not tracking_data or 'eventos' not in tracking_data:
        return False

    has_updates = False

    # Os eventos vêm da API ordenados do mais recente para o mais antigo.
    # Obtemos a lista para processamento.
    api_events_list = tracking_data.get('eventos', [])

    # Iteramos a lista ao contrário (reversed) para inserir na timeline cronologicamente
    # (do evento mais antigo para o mais novo), mantendo a coerência histórica.
    for event_data in reversed(api_events_list):

        description = event_data.get('descricao')
        detail = event_data.get('detalhe', '')

        # Constrói o texto completo para a timeline
        full_description_text = description
        if detail:
            full_description_text += f" - {detail}"

        # Extrai dados da unidade/localização para enriquecer a descrição
        unit_data = event_data.get('unidade', {})
        if 'endereco' in unit_data:
            address = unit_data['endereco']
            location_info = f" ({address.get('cidade', '')}/{address.get('uf', '')})"
            full_description_text += location_info

        # --- VERIFICAÇÃO DE DUPLICIDADE ---
        # Consulta o banco para ver se este evento específico já foi registrado
        event_already_exists = EventoTimeline.objects.filter(
            processo=processo,
            titulo="Rastreio Correios",
            descricao=full_description_text
        ).exists()

        if not event_already_exists:
            # --- MAPA DE ÍCONES E CÓDIGOS ---
            # Define ícones visuais baseados no código do evento (tipo)
            icon_class = "bi-truck"  # Ícone padrão (em trânsito)
            event_code = event_data.get('codigo')
            event_type = event_data.get('tipo')

            # BDE = Baixa de Distribuição (Entrega)
            if event_code == 'BDE' or 'entregue' in description.lower():
                icon_class = "bi-box-seam-fill"
            # OEC = Objeto Saiu para Entrega ao Destinatário
            elif event_code == 'OEC':
                icon_class = "bi-bicycle"
            # PO = Postagem
            elif event_code == 'PO':
                icon_class = "bi-box"

            # Registra o novo evento na timeline do sistema
            EventoTimeline.objects.create(
                processo=processo,
                titulo="Rastreio Correios",
                descricao=full_description_text,
                icone=icon_class,
                autor=None  # Autor é o sistema
            )
            has_updates = True

            # --- AUTOMAÇÃO DE STATUS DO PROCESSO ---

            # Caso 1: Entrega confirmada
            # O código 'BDE' com tipo '01' indica entrega bem sucedida ao destinatário
            if event_code == 'BDE' and event_type == '01':
                if processo.status != 'entregue':
                    processo.status = 'entregue'
                    processo.save()

                    # Adiciona um evento extra informando a mudança de status automática
                    EventoTimeline.objects.create(
                        processo=processo,
                        titulo="Status Atualizado",
                        descricao="Processo finalizado automaticamente via confirmação dos Correios.",
                        icone="bi-check-circle-fill"
                    )

            # Caso 2: Devolução ou Falha na entrega
            # Lógica baseada em texto para capturar recusas ou impossibilidades
            elif 'não entregue' in description.lower():
                if processo.status != 'nao_entregue':
                    processo.status = 'nao_entregue'
                    processo.save()

    return has_updates
