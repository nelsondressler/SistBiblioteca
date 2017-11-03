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

        self.qtdRetornados = 30
        self.qtdRecomendados = 5

        self.procLivros = ProcessamentoLivros('livros', 'livro.Livro')
        self.matrizSimilaridades = procLivros.RecuperarMatrizSimilaridades()

        self.palavrasChave = []
        self.idsSelecionados = []

        self.idsRecomendados = []
        self.ratingRecomendados = []

    #def AtualizarDados(self):
    def CarregarPalavraChaveBD(self, textoPesquisado):
        palavras = textoPesquisado.split(' ')
        stopwords = Stopword.objects.all()

        palavras = [slugify(elemento) for elemento in palavras]
        stopwords = [slugify(elemento) for elemento in stopwords]

        palavras = [elemento.strip() for elemento in palavras if elemento not in stopwords]

        for p in palavras:
            PesquisaPalavraChave.objects.get_or_create(nome = p)
            self.palavrasChave.append(p)

    def SelecionarLivro(self, id):
        self.idsSelecionados.append(id)

    def CarregarRecomendados(self):
        for id in self.idsSelecionados:
            blackList = []
            
            ids = procLivros.CalcularIdsLivrosMaisProximos(id, self.qtdRecomendados, blackList)
            self.idsRecomendados.extend(ids)

    #def CarregarSelecionadosBD(self):
    #def CarregarRecomendadosBD(self):
    #def CarregarRatingsBD(self):
