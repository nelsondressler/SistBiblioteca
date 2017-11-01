from django import forms
from .models import Livro

class PesquisaForm(forms.Form):
    titulo = forms.CharField(label = 'Título', max_length = 500)

class ResultadoForm(forms.Form):
    opcao = forms.MultipleChoiceField()
