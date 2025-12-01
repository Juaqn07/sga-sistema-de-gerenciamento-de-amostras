from django import forms
from django.core.exceptions import ValidationError
import re
from .models import Processo, Cliente, Anexo


class ClienteForm(forms.ModelForm):
    """
    Formulário para cadastro e edição de Clientes.
    Inclui validações customizadas para CEP e campos obrigatórios.
    """
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'estado': forms.TextInput(attrs={'placeholder': 'UF'}),
            'cep': forms.TextInput(attrs={'placeholder': '00000-000'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplica a classe Bootstrap 'form-control' em todos os campos
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

            # Define obrigatoriedade explícita (exceto complemento)
            if field not in ['complemento']:
                self.fields[field].required = True

    # --- VALIDAÇÕES (CLEAN METHODS) ---

    def clean_cep(self):
        """Valida se o CEP contém 8 dígitos numéricos."""
        cep = self.cleaned_data.get('cep', '')
        # Remove caracteres não numéricos (hífen, ponto)
        cep_limpo = re.sub(r'\D', '', cep)

        if not cep_limpo:
            raise ValidationError("O CEP é obrigatório.")

        if len(cep_limpo) != 8:
            raise ValidationError("O CEP deve conter exatamente 8 dígitos.")

        return cep_limpo

    def clean_nome(self):
        """Impede nomes muito curtos."""
        nome = self.cleaned_data.get('nome', '').strip()
        if len(nome) < 3:
            raise ValidationError("O nome deve ter pelo menos 3 caracteres.")
        return nome


class ProcessoForm(forms.ModelForm):
    """
    Formulário principal de criação de processos.
    Gerencia campos condicionais e widgets de upload.
    """

    # Campo de arquivo adicional não vinculado diretamente ao model no save inicial
    arquivo_pedido = forms.FileField(
        required=False,
        label="Anexo do Pedido (Opcional)",
        help_text="Adicione o PDF do pedido ou imagem de referência.",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    # Tratado visualmente como 'Código da Carga' no frontend, mas salvo no campo 'codigo_rastreio'
    codigo_rastreio = forms.CharField(
        required=False,
        label="Código da Carga",
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': 'Informe o código da carga'}
        )
    )

    class Meta:
        model = Processo
        fields = [
            'titulo', 'codigo_pedido_iniflex', 'descricao',
            'tipos_amostra', 'tipo_transporte', 'prioridade',
            'arquivo_pedido', 'codigo_rastreio'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3, 'maxlength': 1000}),
            'tipos_amostra': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            # Aplica form-control, exceto para checkboxes que têm estilo próprio
            if field_name != 'tipos_amostra':
                field.widget.attrs.update({'class': 'form-control'})

            # Ajuste específico para selects (Bootstrap 5)
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})


class AnexoForm(forms.ModelForm):
    """
    Formulário para upload de múltiplos arquivos na tela de detalhes.
    """
    class Meta:
        model = Anexo
        fields = ['arquivo']
        widgets = {
            # 'allow_multiple_selected' permite selecionar vários arquivos na janela do sistema
            'arquivo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'allow_multiple_selected': True
            }),
        }
