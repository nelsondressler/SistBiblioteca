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
            'form': pesquisa,
            'username': request.user.username,
            'pesquisa_id': None
        })

    def post(self, request):
        pesquisa = PesquisaForm(request.POST)

        if pesquisa.is_valid():
            usr = Usuario.objects.first() #request.user
            psq = Pesquisa.objects.create(usuario = usr)

            pesquisa.cleaned_data['pesquisa_id'] = psq.id

            #Salvando as palavras-chave
            titulo = pesquisa.cleaned_data['pesquisa_titulo']
            palavrasChave = self.CarregarPalavrasChaveBD(titulo)

            #Gerando a lista de recuperação
            livrosRecuperados = self.PesquisarPalavraChave(palavrasChave)

            #Formulario será o próximo formulário sempre.
            formulario = SelecaoForm(initial={'pesquisa_titulo': titulo, 'pesquisa_id': psq.id})

            #import pdb; pdb.set_trace()

            return render(request, 'livro/selecao.html', {
                'pesquisa_id': psq.id,
                'form': formulario,
                'livros_recuperados' : livrosRecuperados,
                'username': request.user.username
            })
        else:
            return HttpResponse('Erro em Pesquisa')

class SelecaoView(View):
    def post(self, request):
        selecao = SelecaoForm(request.POST)

        if selecao.is_valid():
            titulo = selecao.cleaned_data['pesquisa_titulo']
            pesquisa_id = selecao.cleaned_data['pesquisa_id']

            livrosSelecionados = selecao.cleaned_data['livros_selecionados']
            livrosRecuperados = []#livros_recuperados #Precisa colocar valor nessa variavel.
            livrosRecomendados = []

            #Salvando selecionados
            #Calculando recomendados

            for livro in livrosRecuperados:
                if livro.id in livrosSelecionados:
                    livro.checked = True
                else:
                    livro.checked = False

            #Formulario será o próximo formulário sempre.
            formulario = RecomendacaoForm(initial={'pesquisa_titulo': titulo, 'pesquisa_id': pesquisa_id, 'livros_selecionados': livrosSelecionados})

            return render(request, 'livro/recomendacao.html', {
                'form': formulario,
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
