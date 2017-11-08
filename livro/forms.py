from django import forms
from .models import Livro

class PesquisaForm(forms.Form):
    titulo = forms.CharField(label = 'Título', max_length = 500)
    pesquisa_id = forms.CharField(required = False, max_length = 50, widget = forms.HiddenInput())

class SelecaoForm(forms.Form):
    livros_selecionados = forms.MultipleChoiceField(widget = forms.CheckboxSelectMultiple)
    pesquisa_titulo = forms.CharField(required = False, max_length = 50, widget = forms.HiddenInput())
    pesquisa_id = forms.CharField(required = False, max_length = 50, widget = forms.HiddenInput())

class RecomendacaoForm(forms.Form):
    livros_recomendados = forms.MultipleChoiceField()
    pesquisa_titulo = forms.CharField(required = False, max_length = 50, widget = forms.HiddenInput())
    pesquisa_id = forms.CharField(required = False, max_length = 50, widget = forms.HiddenInput())
    selecao_livros_selecionados = forms.CharField(required = False, max_length = 50, widget = forms.HiddenInput())
