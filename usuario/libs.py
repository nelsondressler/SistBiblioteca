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

class ProcessamentoUsuarios:
    def __init__(self, usuario, sessao):
        self.qtdTotalDocs = 0
        self.qtdTotalTermos = 0
        self.qtdTotalPesos = 0
        self.qtdTotalSimilaridades = 0

        self.sessao = sessao
        self.usuario = usuario
        self.usuario = Usuario(nome = self.usuario, sessao = self.sessao)
        self.pesquisa = Pesquisa(usuario = usuario)

        self.CadastrarUsuario()
        self.CadastrarPesquisa()

        self.qtdRecuperados = 30
        self.qtdRecomendados = 5

        self.palavrasChave = []
        self.idsRecuperados = []

        self.idsSelecionados = []

        self.idsRecomendados = [] #[(idSelecionado , [idsRecomendados])]
        self.ratingsRecomendados = [] # (like = 1 ou dislike = 0) por livro recomendado
        self.idsBlackList = [] #[(idSelecionado , [idsNegados])]

    def AtualizarDados(self):
        self.qtdTotalDocs = Livro.objects.count()
        self.qtdTotalTermos = Termo.objects.count()
        self.qtdTotalPesos = Peso.objects.count()
        self.qtdTotalSimilaridades = Similaridade.objects.count()

    def LivrosCarregados(self):
        self.AtualizarDados()

        if not self.qtdTotalDocs or not self.qtdTotalTermos or not self.qtdTotalPesos or not self.qtdTotalSimilaridades:
            return False

        return True

    def RecuperarLivrosMaisProximos(self, id, idsNegados):
        livros = Livro.objects.filter(id__in = ids).exclude(livro_j__id = id).order_by('-valor')[:self.qtdRecomendados]
        return livros

    def RecuperarIdsLivrosMaisProximos(self, id, idsNegados):
        ids = Similaridade.objects.filter(livro_i__id = id).exclude(livro_j__id = id).order_by('-valor').values_list('livro_j__id', flat = True)[:self.qtdRecomendados]
        return ids

    def RecuperarValoresLivrosMaisProximos(self, id, idsNegados = []):
        valores = Similaridade.objects.filter(livro_i__id = id).exclude(livro_j__id = id).exclude(livro_j__id__in = idsNegados).order_by('-valor').values_list('valor', flat = True)[:self.qtdRecomendados]
        return valores

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
                self.idsRecuperados = Livro.objects.filter(titulo__unaccent__contains = palavra).values_list('id', flat = True) #"CREATE EXTENSION unaccent;" no PostgreSQL para habilitar o filtro unaccent
            else:
                idLivros = Livro.objects.filter(titulo__unaccent__contains = palavra).values_list('id', flat = True) #"CREATE EXTENSION unaccent;" no PostgreSQL para habilitar o filtro unaccent
                self.idsRecuperados = set(self.idsRecuperados).intersection(idLivros)

        self.idsRecuperados = self.idsRecuperados[:self.qtdRecuperados]

    def SelecionarLivros(self, ids):
        for id in ids:
            self.idsSelecionados.append(id)

    def CarregarIdsNegados(self):
        for idSelecionado in self.idsSelecionados:
            idsPositivos = []
            idsNegativos = PesquisaRecomendacao.objects.filter(selecionado__livro__id = idSelecionado).values_list('recomendado__id', flat = True)
            for idRecomendado in idsNegativos:

                #Avaliações Pessoais (online)
                likesPessoal = PesquisaRecomendacao.objects.filter(selecionado__pesquisa__usuario = self.usuario, selecionado__livro__id = idSelecionado, recomendado__id = idRecomendado, rating = 1).count()
                dislikesPessoal = PesquisaRecomendacao.objects.filter(selecionado__pesquisa__usuario = self.usuario, selecionado__livro__id = idSelecionado, recomendado__id = idRecomendado, rating = 1).count()
                totalPessoal = likes + dislikes
                pesoPessoal = 0.7

                #Avaliações Globais (offline)
                likesGlobal = PesquisaRecomendacao.objects.filter(selecionado__livro__id = idSelecionado, recomendado__id = idRecomendado, rating = 1).count()
                dislikesGlobal = PesquisaRecomendacao.objects.filter(selecionado__livro__id = idSelecionado, recomendado__id = idRecomendado, rating = 1).count()
                totalGlobal = likes + dislikes
                pesoGlobal = 0.3

                avaliacaoTotal = ((dislikesPessoal / totalPessoal) * pesoPessoal) + ((dislikesGlobal / totalGlobal) * pesoGlobal)

                #Se a avaliação total obtiver menos de 50%, o livro recomendado não entra no Blacklist
                if avaliacaoTotal < 0.5:
                    idsPositivos.append(idRecomendado)

            ids = set(idsNegativos).intersection(idsPositivos)

            self.idsBlackList((idSelecionado, ids))

    def CarregarRecomendados(self):
        for idSelecionado, idsNegados in self.idsBlackList:
            ids = self.CalcularIdsLivrosMaisProximos(idSelecionado, idsNegados)
            self.idsRecomendados.append((idSelecionado, ids))

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
