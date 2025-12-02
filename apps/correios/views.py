import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.conf import settings
from apps.samples.models import Processo
from .logic import update_process_tracking
from .services import CorreiosService
from datetime import datetime


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


@login_required
def api_calculate_shipping_view(request, pk):
    """
    Calcula frete chamando APIs distintas de Preço e Prazo e unificando a resposta.
    """
    try:
        processo = get_object_or_404(Processo, pk=pk)
        data = json.loads(request.body)

        # 1. Validação e Extração
        try:
            ps_objeto = data['peso']
            formato = data['formato']
            comprimento = data['comprimento']
            altura = data['altura']
            largura = data['largura']
            valor_declarado = data.get('valor_declarado', '0')
        except KeyError as e:
            return JsonResponse({'status': 'error', 'message': f"Campo faltando: {str(e)}"}, status=400)

        # 2. Configuração CEPs
        cep_origem = getattr(settings, 'CEP_ORIGEM_EMPRESA', None)
        if not cep_origem:
            return JsonResponse({'status': 'error', 'message': "CEP Origem não configurado."}, status=500)

        cep_destino = processo.cliente.cep.replace(
            '-', '').replace('.', '').strip()
        if len(cep_destino) != 8:
            return JsonResponse({'status': 'error', 'message': "CEP destino inválido."}, status=400)

        # 3. Definição dos Serviços
        servicos_para_cotar = [
            {'coProduto': '03220', 'nome': 'SEDEX'},
            {'coProduto': '03298', 'nome': 'PAC'}
        ]

        data_atual = datetime.now().strftime('%d/%m/%Y')

        # 4. Montagem dos Payloads (Separados conforme Manual)

        # Payload PREÇO (Usa 'parametrosProduto')
        lista_preco = []
        # Payload PRAZO (Usa 'parametrosPrazo')
        lista_prazo = []

        for i, servico in enumerate(servicos_para_cotar):
            # Item comum
            base_item = {
                "coProduto": servico['coProduto'],
                "nuRequisicao": str(i + 1),
                "cepOrigem": cep_origem,
                "cepDestino": cep_destino,
                "dtEvento": data_atual
            }

            # Item Específico de Preço (Dimensões, Peso, Valor)
            item_preco = base_item.copy()
            item_preco.update({
                "psObjeto": ps_objeto,
                "tpObjeto": formato,
                "comprimento": comprimento,
                "altura": altura,
                "largura": largura,
                "vlDeclarado": valor_declarado,
            })
            lista_preco.append(item_preco)

            # Item Específico de Prazo (Só precisa dos CEPs e Código)
            item_prazo = base_item.copy()
            lista_prazo.append(item_prazo)

        payload_preco = {"idLote": "1", "parametrosProduto": lista_preco}
        payload_prazo = {"idLote": "1", "parametrosPrazo": lista_prazo}

        # 5. Chamadas aos Serviços
        service = CorreiosService()

        # Chama API Preço
        res_precos = service.calculate_prices(payload_preco)

        # Chama API Prazo
        res_prazos = service.calculate_deadlines(payload_prazo)

        # 6. Unificação dos Resultados
        opcoes_formatadas = []

        # Transforma listas em dicionários indexados pelo 'coProduto' para facilitar busca
        # Ex: {'03220': {dados_sedex...}, '03298': {dados_pac...}}
        mapa_precos = {
            p.get('coProduto'): p for p in res_precos} if res_precos else {}
        mapa_prazos = {
            p.get('coProduto'): p for p in res_prazos} if res_prazos else {}

        for servico in servicos_para_cotar:
            cod = servico['coProduto']

            dados_preco = mapa_precos.get(cod, {})
            dados_prazo = mapa_prazos.get(cod, {})

            # Checa erros individuais
            erro_preco = dados_preco.get(
                'msgErro', '') or dados_preco.get('erro', '')
            # API Prazo as vezes retorna erro em campos diferentes, ajustar conforme teste real

            if erro_preco:
                continue  # Pula se deu erro no cálculo

            opcoes_formatadas.append({
                'servico': servico['nome'],
                'preco': dados_preco.get('pcFinal', '---'),
                'prazo': str(dados_prazo.get('prazoEntrega', '-')),
                'entrega_prevista': dados_prazo.get('dataMaxima', '')
            })

        if not opcoes_formatadas:
            return JsonResponse({'status': 'error', 'message': 'Serviços indisponíveis para este trecho.'})

        return JsonResponse({'status': 'success', 'data': opcoes_formatadas})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
