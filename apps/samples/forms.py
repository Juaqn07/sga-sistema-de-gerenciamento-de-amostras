from django import forms
from .models import Processo, Cliente


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


class ProcessoForm(forms.ModelForm):
    class Meta:
        model = Processo
        # Campos que o usuário preenche (o resto é automático)
        fields = ['titulo', 'descricao', 'tipo_amostra',
                  'tipo_transporte', 'prioridade']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3, 'maxlength': 1000}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            # Adiciona estilo Bootstrap (o form-select do bootstrap é aplicado via classe também)
            self.fields[field].widget.attrs.update({'class': 'form-control'})

            # Ajuste específico para selects ficarem com o estilo nativo do bootstrap
            if isinstance(self.fields[field].widget, forms.Select):
                self.fields[field].widget.attrs.update(
                    {'class': 'form-select'})
