import sys
import os

from django.core.management import call_command
from django.db.models import When, Case, F, IntegerField
from django.utils.text import slugify

from livro.models import Livro, Peso, Similaridade
from stopword.models import Stopword
from usuario.models import Usuario, Pesquisa, PesquisaPalavraChave, PesquisaLivroSelecionado, PesquisaRecomendacao 

import math
import numpy as np

from livro.libs import ProcessamentoLivros

class ProcessamentoUsuarios:
    def __init__(self, usuario, sessao):
        self.sessao = sessao
        self.usuario = usuario
        self.usuario = Usuario(nome = self.usuario, sessao = self.sessao)
        self.pesquisa = Pesquisa(usuario = usuario)

        self.CadastrarUsuario()
        self.CadastrarPesquisa()

        self.qtdRecuperados = 30
        self.qtdRecomendados = 5

        self.procLivros = ProcessamentoLivros('livros', 'livro.Livro')

        procLivros.AtualizarDados()
        if not procLivros.DadosCarregados():
            self.msg = "Favor carregar dados referentes aos livros!"
        else:
            self.procLivros.ProcessarDados()

        self.palavrasChave = []
        self.idsRecuperados = []

        self.idsSelecionados = []

        self.idsRecomendados = []
        self.ratingsRecomendados = [] # (like = 1 ou dislike = 0) por livro recomendado

        self.idsRatingPessoal = [] # (dislikes pessoal / total pessoal) por (livro selecionado x livro recomendado)
        self.idsRatingGlobal = [] # (dislikes global / total global) por (livro selecionado x livro recomendado)
        self.idsNegados = []

    def CadastrarUsuario(self):
        self.usuario.save()

    def CadastrarPesquisa(self):
         self.pesquisa.save()

    def CarregarPalavrasChaveBD(self, textoPesquisado):
        palavras = textoPesquisado.split(' ')
        stopwords = Stopword.objects.all()

        palavras = [slugify(elemento) for elemento in palavras]
        stopwords = [slugify(elemento) for elemento in stopwords]

        palavras = [elemento.strip() for elemento in palavras if elemento not in stopwords]

        for p in palavras:
            PesquisaPalavraChave.objects.create(nome = p, pesquisa = self.pesquisa)
            self.palavrasChave.append(p)

    def PesquisarPalavraChave(self, textoPesquisado):
        self.palavrasChave = []

        self.CarregarPalavrasChaveBD(textoPesquisado)

        for i, palavra in enumerate(self.palavrasChave):
            if i == 0:
                self.idsRecuperados = Livro.objects.filter(titulo__unaccent__contains = palavra).values_list('id', flat = True)
            else:
                idLivros = Livro.objects.filter(titulo__unaccent__contains = palavra).values_list('id', flat = True)
                self.idsRecuperados = set(self.idsRecuperados).intersection(idLivros)

        self.idsRecuperados = self.idsRecuperados[:self.qtdRecuperados]

    def SelecionarLivros(self, ids):
        for id in ids:
            self.idsSelecionados.append(id)

    #def CarregarAvaliacaoPessoal(self):

    #def CarregarAvaliacaoGlobal(self):

    def CarregarRecomendados(self):
        #self.CarregarAvaliacaoPessoal()
        #self.CarregarAvaliacaoGlobal()

        for id in self.idsSelecionados:
            ids = procLivros.CalcularIdsLivrosMaisProximos(id, self.qtdRecomendados, self.idsNegados)
            self.idsRecomendados.extend((id, ids)) #concatenando uma lista com outra

    def SelecionarRatings(self, ratigns):
        for r in ratigns:
            self.ratingsRecomendados.append(r)

    def CarregarSelecionadosBD(self):
        for id in self.idsSelecionados:
            livro = Livro.objects.filter(id = id)
            PesquisaLivroSelecionado.objects.create(livro = livro, pesquisa = self.pesquisa)

    def CarregarRecomendadosBD(self):
        for idSelecionado, ids in self.idsRecomendados:
            livroSelecionado = PesquisaLivroSelecionado.objects.order_by('-id').filter(livro__id = idSelecionado)[:1]
            for id in ids:
                livroRecomendado = Livro.objects.filter(id = id)
                PesquisaRecomendacao.objects.create(selecionado = livroSelecionado, recomendado = livroRecomendado)

    def CarregarRatingsBD(self):
        for i, (idSelecionado, ids) in enumerate(self.idsRecomendados):
            livroSelecionado = PesquisaLivroSelecionado.objects.order_by('-id').filter(livro__id = idSelecionado)[:1]
            for j, id in enumerate(ids):
                livroRecomendado = Livro.objects.filter(id = id)
                recomendacao = PesquisaRecomendacao.objects.order_by('-id').filter(selecionado = livroSelecionado, recomendado = livroRecomendado)[0]
                recomendacao.ratign = self.ratingsRecomendados[i * self.qtdRecomendados + j]
                recomendacao.save()

    #def ProcessarPesquisa(self):
