from django.conf import settings
from django.core.cache import cache
import requests
import base64
from datetime import datetime, timedelta
import logging

# Configura o logger para este módulo
logger = logging.getLogger(__name__)


class CorreiosService:
    """
    Classe responsável por gerenciar a interação com a API CWS dos Correios.
    Documentação oficial: https://cws.correios.com.br/
    """

    # Chave para identificar e armazenar o token de autenticação no cache do Django
    CACHE_KEY = 'correios_api_token'

    def __init__(self):
        """
        Inicializa o serviço carregando as credenciais definidas no settings do Django.
        """
        # Carrega as configurações definidas no settings.py
        credentials = getattr(settings, 'CORREIOS_CREDENTIALS', {})

        self.base_url = credentials.get(
            'url_base', 'https://api.correios.com.br')
        self.api_user = credentials.get('usuario')
        self.api_password = credentials.get('senha')  # Código de Acesso da API
        self.contract_number = credentials.get('contrato')
        self.card_number = credentials.get('cartao')

        # Tenta recuperar um token existente do cache para evitar reautenticação desnecessária
        self._token = cache.get(self.CACHE_KEY)

    def get_token_timeout(self, timeout_date):
        """
        Calcula a duração do timeout do cache em segundos com base em uma string \
        de data/hora de expiração, subtraindo um buffer de segurança de 10 minutos.

        Args:
            timeout_date: Uma string representando o horário de expiração \
            no formato 'YYYY-MM-DDTHH:MM:SS' (ex: '2025-12-01T13:35:50').

        Returns:
            A duração do timeout em segundos (inteiro). Retorna 0 se o tempo de \
            expiração já passou ou for muito próximo (menos de 10 minutos).
        """
        # Define o formato esperado da string de entrada (padrão resposta Correios)
        datetime_format = '%Y-%m-%dT%H:%M:%S'

        # Converte a string de entrada para um objeto datetime
        timeout_date_convert = datetime.strptime(timeout_date, datetime_format)

        # Define o buffer de segurança (10 minutos) usando timedelta
        safety_buffer = timedelta(minutes=10)

        # Calcula o horário exato em que o cache deve expirar (10 minutos antes da expiração real)
        cache_timeout = timeout_date_convert - safety_buffer

        # Calcula a duração restante a partir do horário atual até o horário de expiração do cache
        time_remaining = cache_timeout - datetime.now()

        # Converte a duração restante (timedelta) para o total de segundos como um número inteiro
        timeout_seconds = int(time_remaining.total_seconds())

        # Retorna o resultado, garantindo que o valor mínimo seja 0 (para evitar timeouts negativos no Django)
        return max(0, timeout_seconds)

    def _get_auth_header(self):
        """
        Gera o cabeçalho 'Authorization' no formato Basic Auth para a autenticação inicial.

        Returns:
            Um dicionário contendo o header de autorização codificado em Base64.
        """
        # Concatena usuário e senha no formato padrão exigido (user:password)
        credentials_string = f"{self.api_user}:{self.api_password}"

        # Realiza a codificação em Base64
        encoded_credentials = base64.b64encode(
            credentials_string.encode()).decode()

        return {'Authorization': f'Basic {encoded_credentials}'}

    def authenticate(self):
        """
        Realiza a autenticação na API para obter o Token JWT de acesso via Contrato.
        Endpoint: /token/v1/autentica/contrato

        Returns:
            O token de acesso (string) se a autenticação for bem-sucedida, ou None em caso de falha.
        """
        # Monta a URL completa para o endpoint de autenticação
        auth_url = f"{self.base_url}/token/v1/autentica/contrato"

        # O payload da requisição exige apenas o número do contrato
        payload = {
            "numero": self.contract_number
        }

        # Gera os headers necessários, incluindo a autenticação Basic
        headers = self._get_auth_header()
        headers['Content-Type'] = 'application/json'

        try:
            # Envia a requisição POST com timeout de 10 segundos
            response = requests.post(
                auth_url, json=payload, headers=headers, timeout=10)

            # --- BLINDAGEM ---
            # Verifica se a resposta foi bem-sucedida (Status 200 OK ou 201 Created)
            if response.status_code not in [200, 201]:
                logger.error(
                    f"❌ Erro HTTP na Autenticação: {response.status_code}")
                return None
            # -----------------

            # Processa a resposta JSON
            api_data = response.json()
            self._token = api_data.get('token')

            # Se o token foi recebido, calcula o tempo de vida e salva no cache
            if self._token:
                expiration_str = api_data.get('expiraEm')
                token_timeout_seconds = self.get_token_timeout(expiration_str)

                cache.set(self.CACHE_KEY, self._token,
                          timeout=token_timeout_seconds)

            return self._token

        except Exception as error:
            logger.exception(f"Erro de conexão durante autenticação: {error}")
            return None

    def get_headers(self):
        """
        Retorna os cabeçalhos padrão para chamadas autenticadas, renovando o token se necessário.

        Returns:
            Um dicionário com Authorization (Bearer), Content-Type e Accept.

        Raises:
            Exception: Se não for possível obter um token válido.
        """
        # Verifica se o token existe; se não, tenta autenticar novamente
        if not self._token:
            self.authenticate()

        # Se ainda assim não houver token, lança exceção crítica
        if not self._token:
            logger.critical(
                "Falha crítica: Token dos Correios não pôde ser obtido.")
            raise Exception(
                "Falha crítica: Não foi possível obter token de acesso dos Correios.")

        return {
            'Authorization': f'Bearer {self._token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    # --- MÉTODOS DE SERVIÇO ---

    def consult_zipcode(self, zipcode):
        """
        Consulta informações de endereço via API CWS Correios.
        Endpoint: /cep/v1/enderecos/{cep}

        Args:
            zipcode: O CEP a ser consultado (string ou int), com ou sem formatação.

        Returns:
            Um dicionário contendo logradouro, bairro, cidade, estado e cep.
            Retorna None se o CEP não for encontrado ou houver erro.
        """
        # Remove caracteres não numéricos para garantir o formato correto (8 dígitos)
        sanitized_zipcode = str(zipcode).replace(
            '-', '').replace('.', '').strip()

        if len(sanitized_zipcode) != 8:
            return None

        # Monta a URL de consulta
        endpoint_url = f"{self.base_url}/cep/v1/enderecos/{sanitized_zipcode}"

        try:
            # Obtém headers autenticados
            headers = self.get_headers()

            # Realiza a chamada GET
            response = requests.get(endpoint_url, headers=headers, timeout=10)

            if response.status_code == 200:
                address_data = response.json()

                # Mapeia a resposta da API (que usa 'localidade') para o padrão interno do sistema
                return {
                    'logradouro': address_data.get('logradouro', ''),
                    'bairro': address_data.get('bairro', ''),
                    # Correios usa 'localidade'
                    'cidade': address_data.get('localidade', ''),
                    'estado': address_data.get('uf', ''),
                    'cep': address_data.get('cep', ''),
                    'complemento': address_data.get('complemento', ''),
                }
            elif response.status_code == 404:
                logger.info(
                    f"CEP não encontrado na base Correios: {sanitized_zipcode}")
                return None
            else:
                logger.error(
                    f"Erro API CEP Correios: {response.status_code} - {response.text}")
                return None

        except Exception as error:
            logger.error(f"Erro de conexão (CEP): {error}")
            return None

    def track_object(self, tracking_code):
        """
        Consulta o histórico de eventos de um objeto na API SRO (Rastreamento).

        Args:
            tracking_code: O código de rastreio do objeto (ex: 'AA123456789BR').

        Returns:
            Um dicionário contendo os dados do objeto e a lista de eventos.
            Retorna None se houver erro ou o objeto não for encontrado.
        """
        # Remove caracteres especiais e padroniza para maiúsculas
        sanitized_code = str(tracking_code).replace(
            '-', '').replace('.', '').strip().upper()

        # Monta a URL do endpoint SRO
        endpoint_url = f"{self.base_url}/srorastro/v1/objetos/{sanitized_code}"

        # Parâmetro 'resultado=T' solicita todos os eventos do histórico
        query_params = {'resultado': 'T'}

        try:
            headers = self.get_headers()
            response = requests.get(
                endpoint_url, headers=headers, params=query_params, timeout=15)

            if response.status_code == 200:
                tracking_data = response.json()

                # A API retorna uma estrutura { "objetos": [ ... ] }
                # Verificamos se a lista existe e contém dados
                if 'objetos' in tracking_data and len(tracking_data['objetos']) > 0:
                    object_info = tracking_data['objetos'][0]

                    # Verifica se a API retornou uma mensagem de erro lógica (ex: "Objeto não encontrado")
                    if 'mensagem' in object_info:
                        logger.warning(
                            f"⚠️ Aviso Correios: {object_info['mensagem']}")
                        return None

                    return object_info

            logger.error(
                f"⚠️ Erro API Rastreio: Status {response.status_code} - {response.text}")
            return None

        except Exception as error:
            logger.error(f"❌ Erro conexão Rastreio: {error}")
            return None
