from django import forms
from .models import Livro

class PesquisaForm(forms.Form):
    pesquisa_id = forms.CharField(required = False, max_length = 50, widget = forms.HiddenInput())
    pesquisa_titulo = forms.CharField(label = 'Título', max_length = 500)

class SelecaoForm(forms.Form):
    pesquisa_id = forms.CharField(required = True, max_length = 50, widget = forms.HiddenInput())
    pesquisa_titulo = forms.CharField(label = 'Título', max_length = 500)
    livros_selecionados = forms.MultipleChoiceField(widget = forms.CheckboxSelectMultiple, required = False)

class RecomendacaoForm(forms.Form):
    pesquisa_id = forms.CharField(required = True, max_length = 50, widget = forms.HiddenInput())
    pesquisa_titulo = forms.CharField(label = 'Título', max_length = 500)
    livros_selecionados = forms.MultipleChoiceField(widget = forms.CheckboxSelectMultiple, required = False)
    livros_recomendados = forms.MultipleChoiceField(widget = forms.CheckboxSelectMultiple, required = False)
