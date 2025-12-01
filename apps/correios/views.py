from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from apps.samples.models import Processo
from .logic import update_process_tracking
from .services import CorreiosService


@login_required
def api_tracking_update_view(request, pk):
    """
    Endpoint de API para forçar a atualização de rastreio de um processo específico.
    Geralmente acionado via AJAX pelo botão 'Atualizar Rastreio' no frontend.

    Args:
        request: Objeto HttpRequest padrão do Django.
        pk: Chave primária (ID) do Processo a ser atualizado.

    Returns:
        JsonResponse: Objeto JSON contendo 'status' (success, info, error) e 'message'.
    """
    # Busca o processo ou retorna 404 se não existir
    processo = get_object_or_404(Processo, pk=pk)

    # Validação prévia: processo precisa ter código configurado
    if not processo.codigo_rastreio:
        return JsonResponse({
            'status': 'error',
            'message': "Este processo não possui código de rastreio configurado."
        }, status=400)

    try:
        # Executa a lógica de negócio centralizada
        changes_detected = update_process_tracking(processo)

        if changes_detected:
            return JsonResponse({
                'status': 'success',
                'message': "Rastreamento atualizado! Novas movimentações encontradas."
            })
        else:
            return JsonResponse({
                'status': 'info',
                'message': "Consulta realizada. Nenhuma novidade nos Correios."
            })

    except Exception as error:
        # Captura erros genéricos para não quebrar o frontend, mas retorna status 500
        return JsonResponse({
            'status': 'error',
            'message': f"Erro ao consultar Correios: {str(error)}"
        }, status=500)


@login_required
def api_consult_zipcode_view(request):
    """
    Endpoint de API para consulta de dados de endereço por CEP.
    Utilizada para preenchimento automático de formulários (busca-cep.js).

    Args:
        request: Objeto HttpRequest. Espera-se o parâmetro 'cep' na QueryString (GET).

    Returns:
        JsonResponse: Dados do endereço ou mensagem de erro.
    """
    # Obtém o CEP da query string (ex: ?cep=12345678)
    zipcode_param = request.GET.get('cep', '')

    # Validação básica de tamanho
    if not zipcode_param or len(zipcode_param) < 8:
        return JsonResponse({'status': 'error', 'message': 'CEP inválido.'}, status=400)

    try:
        service = CorreiosService()
        address_data = service.consult_zipcode(zipcode_param)

        # Verifica se houve retorno válido e se não contém flag de erro
        if address_data and 'erro' not in address_data:
            # Mapeia e retorna os dados para consumo do JavaScript
            return JsonResponse({
                'status': 'success',
                'data': {
                    'logradouro': address_data.get('logradouro', ''),
                    'bairro': address_data.get('bairro', ''),
                    'cidade': address_data.get('cidade', ''),
                    'estado': address_data.get('estado', ''),
                    'cep': address_data.get('cep', '')
                }
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'CEP não encontrado.'}, status=404)

    except Exception as error:
        return JsonResponse({'status': 'error', 'message': str(error)}, status=500)
