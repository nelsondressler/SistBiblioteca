from django.views.generic import View

from django.http import HttpResponse
from django.shortcuts import render

from livro.models import Livro, Peso, Similaridade
from stopword.models import Stopword
from usuario.models import Usuario, Pesquisa, PesquisaPalavraChave, PesquisaLivroSelecionado, PesquisaRecomendacao

from .forms import PesquisaForm, SelecaoForm, RecomendacaoForm

import sys
import os

from django.utils.text import slugify

class PesquisaView(View):
    def CarregarPalavrasChaveBD(self, textoPesquisado):
        palavras = textoPesquisado.split(' ')
        stopwords = Stopword.objects.all()

        palavras = [slugify(elemento) for elemento in palavras]
        stopwords = [slugify(elemento) for elemento in stopwords]

        palavras = [elemento.strip() for elemento in palavras if elemento not in stopwords]

        palavrasChave = []

        for p in palavras:
            #PesquisaPalavraChave.objects.create(nome = p, pesquisa = self.pesquisa)
            palavrasChave.append(p)

        return palavrasChave

    def PesquisarPalavraChave(self, palavrasChave):
        for i, palavra in enumerate(palavrasChave):
            if i == 0:
                livrosRecuperados = Livro.objects.filter(titulo__unaccent__icontains = palavra) #"CREATE EXTENSION unaccent;" no PostgreSQL para habilitar o filtro unaccent
            else:
                livros = Livro.objects.filter(titulo__unaccent__icontains = palavra) #"CREATE EXTENSION unaccent;" no PostgreSQL para habilitar o filtro unaccent
                livrosRecuperados = set(livrosRecuperados).intersection(livros)

        return livrosRecuperados

    def get(self, request):
        pesquisa = PesquisaForm()

        return render(request, 'livro/pesquisa.html', {
            'pesquisa_form': pesquisa,
            'username': request.user.username
        })

    def post(self, request):
        pesquisa = PesquisaForm(request.POST)

        if pesquisa.is_valid():
            usr = Usuario.objects.first() #request.user
            psq = Pesquisa(usuario = usr)
            psq.save()

            pesquisa.cleaned_data['pesquisa_id'] = psq.id

            #Salvando as palavras-chave
            titulo = pesquisa.cleaned_data['titulo']
            palavrasChave = self.CarregarPalavrasChaveBD(titulo)

            #Gerando a lista de recuperação
            livrosRecuperados = self.PesquisarPalavraChave(palavrasChave)

            #import pdb; pdb.set_trace()

            return render(request, 'livro/selecao.html', {
                'pesquisa_form': pesquisa,
                'selecao_form': SelecaoForm(),
                'livros_recuperados' : livrosRecuperados,
                'username': request.user.username
            })
        else:
            return HttpResponse('Erro em Pesquisa')

class SelecaoView(View):
    def post(self, request):
        pesquisa = PesquisaForm(request.POST or None)
        selecao = SelecaoForm(request.POST or None)

        if pesquisa.is_valid() and selecao.is_valid():
            titulo = pesquisa.cleaned_data['pesquisa_titulo']
            pesquisa_id = pesquisa.cleaned_data['pesquisa_id']

            livrosRecuperados = livros_recuperados
            livrosSelecionados = selecao.cleaned_data['livros_selecionados']
            livrosRecomendados = []

            #Salvando selecionados
            #Calculando recomendados

            for livro in livrosRecuperados:
                if livro.id in livrosSelecionados:
                    livro.checked = True
                else:
                    livro.checked = False

            return render(request, 'livro/recomendacao.html', {
                'pesquisa_form': pesquisa,
                'selecao_form': SelecaoForm(livrosSelecionados, titulo, pesquisa_id),
                'recomendacao_form': RecomendacaoForm(livrosRecomendados, titulo, pesquisa_id, livrosSelecionados),
                'livros_selecionados': livrosSelecionados,
                'livros_recomendados': livrosRecomendados,
                'username': request.user.username
            })
        else:
            return HttpResponse('Erro em Seleção')

class RecomendacaoView(View):
    def post(self, request):
        pesquisa = PesquisaForm(request.POST or None)
        selecao = SelecaoForm(request.POST or None)
        recomendacao = RecomendacaoForm(request.POST or None)

        if pesquisa.is_valid() and selecao.is_valid() and recomendacao.is_valid():
            #Salvando avaliação

            return render(request, 'livro/avaliacao.html')
        else:
            pass
