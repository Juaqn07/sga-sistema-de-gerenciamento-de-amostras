from django import forms
from .models import Processo, Cliente, Anexo


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'estado': forms.TextInput(attrs={'placeholder': 'UF'}),
            'cep': forms.TextInput(attrs={'placeholder': '00000-000'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona estilo Bootstrap a todos os campos
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            self.fields[field].required = False


class ProcessoForm(forms.ModelForm):

    arquivo_pedido = forms.FileField(
        required=False,
        label="Anexo do Pedido (Opcional)",
        help_text="Adicione o PDF do pedido ou imagem de referência.",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Processo
        # Campos que o usuário preenche (o resto é automático)
        fields = ['titulo', 'codigo_pedido_iniflex',
                  'descricao', 'tipos_amostra', 'tipo_transporte', 'prioridade', 'arquivo_pedido']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3, 'maxlength': 1000}),
            'tipos_amostra': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # CORREÇÃO: Só aplica 'form-control' se NÃO for os checkboxes
            if field_name != 'tipos_amostra':
                field.widget.attrs.update({'class': 'form-control'})

            # Ajuste específico para selects
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})


class AnexoForm(forms.ModelForm):
    class Meta:
        model = Anexo
        fields = ['arquivo']
        widgets = {
            # O segredo está aqui: 'multiple': True permite selecionar vários arquivos na janela
            'arquivo': forms.ClearableFileInput(attrs={'class': 'form-control', 'allow_multiple_selected': True}),
        }
