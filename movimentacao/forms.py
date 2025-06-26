from django import forms
from movimentacao.models import Movimentacao

class TrocaCurralForm(forms.ModelForm):
    class Meta:
        model = Movimentacao
        fields = ['data_movimentacao', 'status', 'lote_origem', 'lote_destino', 'curral_destino']
        widgets = {
            'data_movimentacao': forms.DateInput(attrs={'type': 'date'}),
        }

