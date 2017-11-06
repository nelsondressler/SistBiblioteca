import sys
import os

from django.core.management import call_command
from django.db.models import When, Case, F, IntegerField
from django.utils.text import slugify

from livro.models import Livro, Peso, Similaridade
from stopword.models import Stopword
from usuario.models import Usuario, PesquisaPalavraChave, Pesquisa, Recomendacao

import math
import numpy as np

from livro.libs import ProcessamentoLivros

class ProcessamentoUsuarios:
    def __init__(self, usuario, sessao):
        self.sessao = sessao
        self.usuario = usuario

        self.qtdRecuperados = 30
        self.qtdRecomendados = 5

        self.procLivros = ProcessamentoLivros('livros', 'livro.Livro')

        procLivros.AtualizarDados()
        if not procLivros.DadosCarregados():
            msg = "Favor carregar dados referentes aos livros!"
        else:
            procLivros.ProcessarDados()

        self.palavrasChave = []
        self.idsRecuperados = []

        self.idsSelecionados = []

        self.idsRecomendados = []
        self.ratingsRecomendados = [] # (like = 1 ou dislike = 0) por livro recomendado

        self.idsRatingPessoal = [] # (dislikes pessoal / total pessoal) por (livro selecionado x livro recomendado)
        self.idsRatingGlobal = [] # (dislikes global / total global) por (livro selecionado x livro recomendado)
        self.idsNegados = []

    #def AtualizarDados(self):
    def CarregarPalavrasChaveBD(self, textoPesquisado):
        palavras = textoPesquisado.split(' ')
        stopwords = Stopword.objects.all()

        palavras = [slugify(elemento) for elemento in palavras]
        stopwords = [slugify(elemento) for elemento in stopwords]

        palavras = [elemento.strip() for elemento in palavras if elemento not in stopwords]

        for p in palavras:
            PesquisaPalavraChave.objects.get_or_create(nome = p)
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
            self.idsRecomendados.extend(ids) #concatenando uma lista com outra

    def SelecionarRatings(self, ratigns):
        for r in ratigns:
            self.ratingsRecomendados.append(r)

    #def CarregarSelecionadosBD(self):
    #def CarregarRecomendadosBD(self):
    #def CarregarRatingsBD(self):
