import sys
import os

from django.core.management import call_command
from django.db.models import When, Case, F, IntegerField
from django.utils.text import slugify

from livro.models import Livro, Peso, Similaridade
from termo.models import Termo
from stopword.models import Stopword
from usuario.models import Usuario, Pesquisa, PesquisaPalavraChave, PesquisaLivroSelecionado, PesquisaRecomendacao

class ProcessamentoUsuarios:
    def __init__(self, username, nome, sobrenome, email):
        self.qtdTotalDocs = 0
        self.qtdTotalTermos = 0
        self.qtdTotalPesos = 0
        self.qtdTotalSimilaridades = 0

        self.usuario = Usuario(username = username, first_name = nome, last_name = sobrenome, email = email, is_staff = True, is_active = True)
        self.CadastrarUsuario()

        self.pesquisa = Pesquisa(usuario = self.usuario)

        self.qtdRecuperados = 10
        self.qtdRecomendados = 2

        self.palavrasChave = []
        self.idsRecuperados = []

        self.idsSelecionados = []

        self.idsRecomendados = [] #[(idSelecionado , [idsRecomendados])]
        self.ratingsRecomendados = [] # (like = 1 ou dislike = 0) por livro recomendado
        self.idsBlackList = [] #[(idSelecionado , [idsNegados])]

        self.AtualizarDados()

        if not self.LivrosCarregados():
            print('Favor carregar os livros, pesos e similaridades na base...')

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

    def UsuarioExistente(self):
        qtdUsuarios = Usuario.objects.filter(username = self.usuario.username).count()

        if qtdUsuarios:
            return True

        return False

    def CadastrarUsuario(self):
        print('\n')

        if self.UsuarioExistente():
            self.usuario = Usuario.objects.filter(username = self.usuario.username)[0]
            print('Usuário selecionado:')
        else:
            self.usuario.save()
            print('Novo usuário cadastrado:')

        print('ID: ' + str(self.usuario.id))
        print('Nome: ' + self.usuario.first_name)
        print('Sobrenome: ' + self.usuario.last_name)
        print('Login: ' + self.usuario.username)
        print('Email: ' + self.usuario.email)
        print('\n')

    def CadastrarPesquisa(self):
         self.pesquisa.save()
         print('\n')
         print('Nova pesquisa cadastrada:')
         print('ID: ' + str(self.pesquisa.id))
         print('Login: ' + self.usuario.username)

    def RecuperarLivrosMaisProximos(self, id, idsNegados):
        livros = Livro.objects.filter(id__in = ids).exclude(livro_j__id = id).exclude(livro_j__id__in = self.idsSelecionados).exclude(livro_j__id__in = idsNegados).order_by('-valor')[:self.qtdRecomendados]
        return livros

    def RecuperarIdsLivrosMaisProximos(self, id, idsNegados):
        ids = Similaridade.objects.filter(livro_i__id = id).exclude(livro_j__id = id).exclude(livro_j__id__in = self.idsSelecionados).exclude(livro_j__id__in = idsNegados).order_by('-valor').values_list('livro_j__id', flat = True)[:self.qtdRecomendados]
        return ids

    def RecuperarValoresLivrosMaisProximos(self, id, idsNegados = []):
        valores = Similaridade.objects.filter(livro_i__id = id).exclude(livro_j__id = id).exclude(livro_j__id__in = self.idsSelecionados).exclude(livro_j__id__in = idsNegados).order_by('-valor').values_list('valor', flat = True)[:self.qtdRecomendados]
        return valores

    def CarregarPalavrasChaveBD(self, textoPesquisado):
        palavras = textoPesquisado.split(' ')
        stopwords = Stopword.objects.all()

        palavras = [slugify(elemento) for elemento in palavras]
        stopwords = [slugify(elemento) for elemento in stopwords]

        palavras = [elemento.strip() for elemento in palavras if elemento not in stopwords]

        for p in palavras:
            PesquisaPalavraChave.objects.create(nome = p, pesquisa = self.pesquisa)
            self.palavrasChave.append(p)

    def CarregarIdsNegados(self):
        for idSelecionado in self.idsSelecionados:
            idsPositivos = []
            idsNegativos = PesquisaRecomendacao.objects.filter(selecionado__livro__id = idSelecionado).values_list('recomendado__id', flat = True)
            for idRecomendado in idsNegativos:

                #Avaliações Pessoais (online)
                likesPessoal = PesquisaRecomendacao.objects.filter(selecionado__pesquisa__usuario = self.usuario, selecionado__livro__id = idSelecionado, recomendado__id = idRecomendado, rating = True).count()
                dislikesPessoal = PesquisaRecomendacao.objects.filter(selecionado__pesquisa__usuario = self.usuario, selecionado__livro__id = idSelecionado, recomendado__id = idRecomendado, rating = False).count()
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

            self.idsBlackList.append((idSelecionado, ids))

    def CarregarRecomendados(self):
        #self.CarregarIdsNegados()
        self.idsRecomendados = []
        self.idsBlackList = []
        idsNegados =[]

        for idSelecionado in self.idsSelecionados:
            self.idsBlackList.append((idSelecionado, idsNegados))

        for idSelecionado, idsNegados in self.idsBlackList:
            ids = self.RecuperarIdsLivrosMaisProximos(idSelecionado, idsNegados)
            self.idsRecomendados.append((idSelecionado, ids))

    def CarregarSelecionadosBD(self):
        for id in self.idsSelecionados:
            livro = Livro.objects.get(id = id)
            PesquisaLivroSelecionado.objects.create(livro = livro, pesquisa = self.pesquisa)

    def CarregarRecomendadosBD(self):
        for idSelecionado, ids in self.idsRecomendados:
            livroSelecionado = PesquisaLivroSelecionado.objects.order_by('-id').filter(livro__id = idSelecionado)[0]
            for id in ids:
                livroRecomendado = Livro.objects.get(id = id)
                PesquisaRecomendacao.objects.create(selecionado = livroSelecionado, recomendado = livroRecomendado)

    def CarregarRatingsBD(self):
        for i, (idSelecionado, ids) in enumerate(self.idsRecomendados):
            livroSelecionado = PesquisaLivroSelecionado.objects.order_by('-id').filter(livro__id = idSelecionado)[0]
            for j, id in enumerate(ids):
                livroRecomendado = Livro.objects.filter(id = id)
                recomendacao = PesquisaRecomendacao.objects.order_by('-id').filter(selecionado = livroSelecionado, recomendado = livroRecomendado)[0]
                if self.ratingsRecomendados[i * self.qtdRecomendados + j]:
                    recomendacao.rating = True
                else:
                    recomendacao.rating = False
                recomendacao.save()

    def ApresentarLivrosRecuperados(self):
        print('\n')
        if self.idsRecuperados:
            print('Livros Recuperados:')
            for id in self.idsRecuperados:
                livro = Livro.objects.get(id = id)
                print('[' + str(livro.id) + '] ' + livro.titulo)
        else:
            print('Nenhum livro recuperado.')
        print('\n')

    def ApresentarLivrosSelecionados(self):
        print('\n')
        if self.idsSelecionados:
            print('Livros Selecionados:')
            for id in self.idsSelecionados:
                livro = Livro.objects.get(id = id)
                print('[' + str(livro.id) + '] ' + livro.titulo)
        else:
            print('Nenhum livro selecionado.')
        print('\n')

    def ApresentarLivrosRecomendados(self):
        print('\n')
        if self.idsRecomendados:
            for idSelecionado, ids in self.idsRecomendados:
                livroSelecionado = Livro.objects.get(id = idSelecionado)
                print('\nLivro Selecionado: [' + str(livroSelecionado.id) + '] ' + livroSelecionado.titulo)
                print('Livros Recomendados:')

                for idRecomendado in ids:
                    livroRecomendado = Livro.objects.get(id = idRecomendado)
                    print('[' + str(livroRecomendado.id) + '] ' + livroRecomendado.titulo)
        else:
            print('Nenhum livro recomendado.')
        print('\n')

#-----------------------------------------------------------------------------------------------------------------------

    def PesquisarPalavraChave(self, textoPesquisado):
        resultado = False

        self.CadastrarPesquisa()

        print('Campo pesquisa: ' + textoPesquisado)

        self.palavrasChave = []

        self.CarregarPalavrasChaveBD(textoPesquisado)

        for i, palavra in enumerate(self.palavrasChave):
            if i == 0:
                self.idsRecuperados = Livro.objects.filter(titulo__unaccent__icontains = palavra).values_list('id', flat = True) #"CREATE EXTENSION unaccent;" no PostgreSQL para habilitar o filtro unaccent
            else:
                idLivros = Livro.objects.filter(titulo__unaccent__icontains = palavra).values_list('id', flat = True) #"CREATE EXTENSION unaccent;" no PostgreSQL para habilitar o filtro unaccent
                self.idsRecuperados = list(set(self.idsRecuperados).intersection(idLivros))

        self.idsRecuperados = self.idsRecuperados[:self.qtdRecuperados]

        self.ApresentarLivrosRecuperados()

        if self.idsRecuperados:
            resultado = True

        return resultado

    def SelecionarLivros(self, ids):
        selecionado = False

        for id in ids:
            if id in self.idsRecuperados:
                if id not in self.idsSelecionados:
                    self.idsSelecionados.append(id)
                    selecionado = True
                else:
                    print('[Erro] O ID ' + str(id) + ' já aparece na lista de seleção.')
            else:
                print('[Erro] O ID ' + str(id) + ' não apareceu no resultado da pesquisa. Favor colocar um ID válido.')

        self.ApresentarLivrosSelecionados()

        return selecionado

    def DesmarcarLivros(self, ids):
        for id in ids:
            if id in self.idsSelecionados:
                self.idsSelecionados.remove(id)
            else:
                print('[Erro] O ID ' + str(id) + ' não foi selecionado.')

        self.ApresentarLivrosSelecionados()

    def LimparSelecao(self):
        self.idsSelecionados = []

    def EnviarLivrosSelecionados(self):
        self.CarregarSelecionadosBD()
        self.CarregarRecomendados()
        self.CarregarRecomendadosBD()
        self.ApresentarLivrosRecomendados()
        self.LimparSelecao()

    def ExplorarLivro(self, id):
        livro = Livro.objects.get(id = id)
        print('\n')
        print('ID: ' + str(livro.id))
        print('Título: ' + livro.titulo)
        print('Autor(es): ' + livro.autor)
        print('Editora: ' + livro.editora)
        print('Ano de Publicação: ' + str(livro.ano_publicacao))
        print('Descrição: ' + livro.descricao)
        print('\n')

    def EnviarRatings(self, ratings):
        self.ratingsRecomendados = []

        avaliado = False

        qtdRecomendados = 0
        for idsSelecionados, idsRecomendados in self.idsRecomendados:
            qtdRecomendados = qtdRecomendados + len(idsRecomendados)

        if len(ratings) == qtdRecomendados:
            for r in ratings:
                self.ratingsRecomendados.append(r)

            self.CarregarRatingsBD()

            self.idsSelecionados = []
            self.idsRecomendados = []

            print('\n')
            print('Avaliação recebida com sucesso! Muito obrigado pela sua colaboração...')
            print('\n')
            print('Nova pesquisa?')
            avaliado = True

        else:
            print('[Erro] O número de ratings não corresponde a quantidade de livros recomendados. Favor avaliar novamente.')

        return avaliado
