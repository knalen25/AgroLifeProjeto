from django import forms

class PeriodoForm(forms.Form):
    data_inicio = forms.DateField(label="Data Inicial", widget=forms.DateInput(attrs={'type': 'date'}))
    data_fim = forms.DateField(label="Data Final", widget=forms.DateInput(attrs={'type': 'date'}))
