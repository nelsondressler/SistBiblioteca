import sys
import os
import re

import csv
import codecs
import json
from stop_words import get_stop_words

from django.core.management import call_command
from django.db.models import When, Case, F, IntegerField, FloatField
from django.utils.text import slugify

from livro.models import Livro, Peso, Similaridade
from termo.models import Termo
from stopword.models import Stopword

from apiclient.discovery import build
from googleapiclient.errors import HttpError

import math
import numpy as np

class ProcessamentoLivros:
    LIVROS_M, TERMOS_N, FREQUENCIAS, TFS, IDFS, TFIDFS, MEDIAS, PESOS, SIMILARIDADES = range(9)

    def __init__(self, nomeArquivo, modelo = 'livro.Livro'):
        self.encoding = 'utf8'
        self.delimitador = ';'
        self.nomeArquivoCSV = nomeArquivo + '.csv'
        self.nomeArquivoJSON = nomeArquivo + '.json'
        self.caminhoCSV = os.path.abspath('../dados/')
        self.caminhoJSON = os.path.abspath('livro/fixtures/')
        self.arquivoCSV = self.caminhoCSV + '\\' + self.nomeArquivoCSV
        self.arquivoJSON = self.caminhoJSON + '\\' + self.nomeArquivoJSON
        self.modelo = modelo

        self.qtdTotalDocs = 0
        self.qtdTotalTermos = 0

        self.termoIds = []
        self.livroIds = []

        self.qtdLivrosPorTermos = []
        self.qtdTermosPorLivros = []

        self.matrizFrequencias = []
        self.matrizTF = []
        self.matrizIDF = []
        self.matrizTFIDF = []
        self.medias = []
        self.matrizPesos = []
        self.matrizSimilaridades = []

    def AtualizarDados(self):
        self.qtdTotalDocs = Livro.objects.count()
        self.qtdTotalTermos = Termo.objects.count()

        self.termoIds = Termo.objects.order_by('id').values_list('id', flat = True)
        self.livroIds = Livro.objects.order_by('id').values_list('id', flat = True)

        self.CarregarQtds()

    def CarregarQtds(self):
        termos = Termo.objects.order_by('id').values_list('nome', flat = True)
        livros = Livro.objects.order_by('id').values_list('conteudo_processado', flat = True)

        self.qtdLivrosPorTermos = []
        self.qtdTermosPorLivros = []

        for termo in termos:
            qtd = 0

            for livro in livros:
                if termo in livro:
                    qtd = qtd + 1

            self.qtdLivrosPorTermos.append(qtd)

        for livro in livros:
            palavras = livro.split(" ")
            qtd = len(palavras)
            self.qtdTermosPorLivros.append(qtd)


    def ConsultarDescricao(self, isbn):
        chaveApiGoogle = 'AIzaSyDzGpl0S6cQi8uxtb8Q3aEX56k7gsDO6K4' #nelsondr58@gmail.com
        campo = 'ISBN:'
        consulta = campo + str(isbn)
        servico = build('books', 'v1', developerKey = chaveApiGoogle)
        requisicao = servico.volumes().list(source = 'public', q = consulta)

        try:
            resultado = requisicao.execute()

            dadosLivroJSON = json.dumps(resultado)
            dadosLivroDict = json.loads(dadosLivroJSON)

            if int(dadosLivroDict['totalItems']) > 0 and 'description' in dadosLivroDict['items'][0]['volumeInfo']:
                descricao = dadosLivroDict['items'][0]['volumeInfo']['description']
            else:
                descricao = ''
        except HttpError as e:
            if e.resp.status in [403, 500, 503]:
                print(e)
                descricao = False

        return descricao

    def GerarArquivoJSON(self):
        entrada = self.arquivoCSV
        saida = self.arquivoJSON

        print('Convertendo de CSV para JSON')
        print('Arquivo de entrada: %s' % (entrada))
        print('Arquivo de saída: %s' % (saida))

        with codecs.open(entrada, 'r', encoding = self.encoding) as arquivo:
            conteudoCSV = csv.reader(arquivo, delimiter = self.delimitador)

            cabecalhos = []
            isbnsCadastrados = []

            #Caso exista o arquivo json
            try:
                listaLivros = json.load(open(saida, encoding = self.encoding))
                id = len(listaLivros) + 1
                for dadosLivro in listaLivros:
                    isbnsCadastrados.append(dadosLivro['fields']['isbn'])
                print('Existe!')
            except IOError as e:
                listaLivros = []
                id = 1
                print('Não Existe!')

            for registro in conteudoCSV:

              if not cabecalhos:
                cabecalhos = registro
                continue

              pk = id
              campos = {}

              for i in range(len(registro)):
                  if i == 0:
                      campos[cabecalhos[i]] = registro[i].strip().replace('.','').replace('-','')[0:13]
                  else:
                      campos[cabecalhos[i]] = registro[i].strip()


              #O campo ano_publicacao deve ser inteiro
              try:
                  campos[cabecalhos[4]] = int(campos[cabecalhos[4]])
              except ValueError:
                  campos[cabecalhos[4]] = 0

              if not campos[cabecalhos[0]] in isbnsCadastrados:
                  print('Processando o livro de ISBN: ' + campos[cabecalhos[0]])
                  descricao = self.ConsultarDescricao(campos[cabecalhos[0]])

                  if descricao == False:
                      break

                  campos['descricao'] = descricao
                  l = {}
                  l['pk'] = pk
                  l['model'] = self.modelo
                  l['fields'] = campos
                  listaLivros.append(l)
                  isbnsCadastrados.append(l['fields'][cabecalhos[0]])

                  print('ID adicionado: ' + str(id))
              else:
                  continue

              id = id + 1

        arquivo.close()

        with codecs.open(saida, 'w', encoding = self.encoding) as arquivo:
            arquivo.write('%s' % json.dumps(listaLivros, indent = 4, ensure_ascii = False))
        arquivo.close()

    def CarregarFixturesBD(self):
        Livro.objects.all().delete()
        call_command('loaddata', self.arquivoJSON)
        qtdeVazios = Livro.objects.filter(descricao__exact='').count()
        Livro.objects.filter(descricao__exact='').delete()
        print('%d livros com descrição vazia excluídos' % (qtdeVazios))

    def CarregarStopWordsBD(self):
        br_stopwords = get_stop_words('portuguese') #lista de stopwords em português
        #en_stopwords = get_stop_words('en') #lista de stopwords em inglês

        for termo in br_stopwords:
            Stopword.objects.get_or_create(nome = termo)

    def CarregarTermosBD(self):
        for livro in Livro.objects.order_by('id'):
            #Gerando as listas de palavras de cada documento e as stopwords
            palavras = livro.descricao.split(' ')
            stopwords = Stopword.objects.all()

            #Convertendo todas as letras para minúsculo e eliminando caracteres especiais e acentuação
            palavras = [slugify(elemento) for elemento in palavras]
            stopwords = [slugify(elemento) for elemento in stopwords]

            #Eliminando todas as stopwords em todas as palavras do documento
            palavras = [elemento.strip() for elemento in palavras if elemento not in stopwords]

            livro.conteudo_processado = ' '.join(palavras)
            livro.save()

            for p in palavras:
                Termo.objects.get_or_create(nome = p)

        self.AtualizarDados()

    def CarregarMatrizFrequencias(self):
        termos = Termo.objects.order_by('id')

        mF = []

        for i, (documento, id) in enumerate(Livro.objects.order_by('id').values_list('conteudo_processado', 'id')):
            palavras = documento.split(" ")

            colunas = []
            for j, termo in enumerate(termos):
                frequencia = 0

                for p in palavras:
                    #Normaliza para minuscula para comparar case insensitive
                    if termo.nome.lower() == p.lower():
                        frequencia += 1

                colunas.append(frequencia)
                #print('F(' + str(i) + ',' + str(j) + ') = ' + str(frequencia))

            mF.append(colunas)
            print('[Frequencias] Livro ' + str(id) + ' calculado.')

        self.matrizFrequencias = np.matrix(mF) #Matriz do numpy

    def CarregarMatrizTF(self):
        mTF = []

        for i, idLivro in enumerate(self.livroIds):
            colunas = []

            for j, idTermo in enumerate(self.termoIds):
                tf = self.matrizFrequencias[i,j] / self.qtdTermosPorLivros[i]

                colunas.append(tf)
                #print('TF(' + str(i) + ',' + str(j) + ') = ' + str(tf))

            #Gravando as linhas (conjunto de colunos) na matriz de TF
            mTF.append(colunas)
            print('[TFs] Livro ' + str(idLivro) + ' calculado.')

        self.matrizTF = np.matrix(mTF) #Matriz do numpy

    def CarregarMatrizIDF(self):
        mIDF = []

        for i, idLivro in enumerate(self.livroIds):
            colunas = []

            for j, idTermo in enumerate(self.termoIds):
                idf = math.log10(self.qtdTotalDocs / self.qtdLivrosPorTermos[j])

                colunas.append(idf)
                #print('IDF(' + str(i) + ',' + str(j) + ') = ' + str(idf))

            #Gravando as linhas (conjunto de colunos) na matriz de TF
            mIDF.append(colunas)
            print('[IDFs] Livro ' + str(idLivro) + ' calculado.')

        self.matrizIDF = np.matrix(mIDF) #Matriz do numpy

    def CarregarMatrizTFIDF(self):
        self.matrizTFIDF = np.multiply(self.matrizTF, self.matrizIDF)
        print('[TFIDFs] Livros calculado(s):\n' + str(self.livroIds))

    def CarregarVetorMedias(self):
        vM = []

        for i, idLivro in enumerate(self.livroIds):
            vM.append(np.sqrt(np.sum(np.power(self.matrizTFIDF[i], 2))))
            print('[Médias] Livro ' + str(idLivro) + ' calculado.')

        self.medias = np.array(vM)

    def CarregarMatrizPesos(self):
        mP = []

        for i, idLivro in enumerate(self.livroIds):
            colunas = []

            for j, idTermo in enumerate(self.termoIds):
                peso = self.matrizTFIDF[i,j] / self.medias[i]

                colunas.append(peso)
                #print('W(' + str(i) + ',' + str(j) + ') = ' + str(peso))

            mP.append(colunas)
            print('[Pesos] Livro ' + str(idLivro) + ' calculado.')

        self.matrizPesos = np.matrix(mP) #Matriz do numpy

    def CarregarPesosBD(self):
        for i, idLivro in enumerate(self.livroIds):
            livro = Livro.objects.get(id = idLivro)
            for j, idTermo in enumerate(self.termoIds):
                termo = Termo.objects.get(id = idTermo)
                if self.matrizPesos[i,j]:
                    Peso.objects.get_or_create(livro = livro, termo = termo, valor = self.matrizPesos[i,j])
                    print('[BD] Peso[' + str(idLivro) + ',' + str(idTermo) + ']' + ' inserido.')

    def ProcessarPesos(self):
        #(1) Valores de totais, ids de livros, ids de termos, qtd de termos por documento, qtd de documentos por termo
        self.AtualizarDados()

        #(2) Matriz de Frequências
        self.CarregarMatrizFrequencias()

        #(1) Matriz de TFs
        self.CarregarMatrizTF()

        #(2) Matriz de IDFs
        self.CarregarMatrizIDF()

        #(3) Matriz de TFIDFs
        self.CarregarMatrizTFIDF()

        #(4) Vetor de Medias
        self.CarregarVetorMedias()

        #(5) Matriz de Pesos
        self.CarregarMatrizPesos()

        #(6) Pesos -> BD
        self.CarregarPesosBD()

    def RecuperarMatrizPesos(self):
        m = []

        #Opção 1: ineficiente
        #for idLivro in procLivros.livroIds:
            #colunas = []

            #for idTermo in procLivros.termoIds:
                #try:
                    #colunas.append(Peso.objects.filter(livro__id = idLivro, termo__id = idTermo)[0].valor)
                #except:
                    #colunas.append(0)

            #print('[Pesos] Livro ' + str(idLivro) + ' carregado.')
            #m.append(colunas)

        #Opção 2: eficiente
        for idLivro in self.livroIds:
            m.append(Termo.objects.order_by('id').annotate(pesoij = Case(When(peso__livro_id = idLivro, then = 'peso__valor'), default = 0, output_field = FloatField())).values_list('pesoij', flat = True))
            print('[Pesos] Livro ' + str(idLivro) + ' carregado.')

        self.matrizPesos = np.matrix(m)

    def CarregarMatrizSimilaridades(self):
        mSimilaridades = []

        for i, idLivroI in enumerate(self.livroIds):
            colunas = []
            for j, idLivroJ in enumerate(self.livroIds):
                #Acumulando os somatórios de D(i,j), D(i) e D(j)
                somatorioDiDj = np.sum(np.multiply(self.matrizPesos[i], self.matrizPesos[j]))
                somatorioDi = np.sum(np.power(self.matrizPesos[i], 2))
                somatorioDj = np.sum(np.power(self.matrizPesos[j], 2))

                #Calculando a similaridade de D(i,j)
                similaridadeIJ = somatorioDiDj / math.sqrt(somatorioDi, somatorioDj)

                colunas.append(similaridadeIJ)

            mSimilaridades.append(colunas)
            print('[Similaridades] Livro ' + str(idLivroI) + ' calculado.')

        self.matrizSimilaridades = np.matrix(mSimilaridades)

    def CarregarSimilaridadesBD(self):
        for i, idLivroI in enumerate(self.livroIds):
            livroI = Livro.objects.get(id = idLivroI)
            for j, idLivroJ in enumerate(self.livroIds):
                livroJ = Livro.objects.get(id = idLivroJ)
                if self.matrizSimilaridades[i,j]:
                    Similaridade.objects.get_or_create(livro_i = idLivroI, livro_j = idLivroJ, valor = self.matrizSimilaridades[i,j])
                    print('[BD] Peso[' + str(idLivroI) + ',' + str(idTermoJ) + ']' + ' inserido.')

    def ProcessarSimilaridades(self):
        #(1) Valores de totais, IDs MxN, IDs MxM
        self.AtualizarDados()

        #(2) Matriz de Similaridades
        self.CarregarMatrizSimilaridades()

        #(6) Similaridades -> BD
        self.CarregarSimilaridadesBD()

    def RecuperarMatrizSimilaridades(self):
        m = []

        for idLivroI in self.livroIds:
            m.append(Livro.objects.order_by('id').annotate(sim = Case(When(similaridade__livro_i_id = idLivroI, then = 'similaridade__valor'), default = 0, output_field = FloatField())).values_list('sim', flat = True))

        self.matrizSimilaridades = np.matrix(m)

    def CalcularIdsLivrosMaisProximos(self, id, qtde, blackList):
        ids = Similaridade.objects.filter(livro_i__id = id).exclude(livro_j__id__in = blackList).order_by('-valor').value_list('livro_j__id')[:n]
        return ids

    def CalcularLivrosMaisProximos(self, id, qtde):
        livros = Livro.objects.filter(similaridade_livro_i__id = id).order_by('-similaridade__valor').value_list('similaridade_livro_j')[:n]
        return livros

    def ExibirIds(self, tipo):
        #Tipos: LIVROS_M, TERMOS_N
        if tipo == self.TERMOS_N:
            print(self.livroIds)
        elif tipo == self.LIVROS_M:
            print(self.termoIds)
        else:
            print('Tipo incorreto!')

    def ExibirVetor(self, tipo):
        #Tipos: MEDIAS
        if tipo == self.MEDIAS:
            print(self.medias)
        else:
            print('Tipo incorreto!')

    def ExibirMatriz(self, tipo):
        #Tipos: FREQUENCIAS, TFS, IDFS, TFIDFS, PESOS, SIMILARIDADES
        if tipo == self.FREQUENCIAS:
            print(self.matrizFrequencias)
        elif tipo == self.TFS:
            print(self.matrizTF)
        elif tipo == self.IDFS:
            print(self.matrizIDF)
        elif tipo == self.TFIDFS:
            print(self.matrizTFIDF)
        elif tipo == self.PESOS:
            print(self.matrizPesos)
        elif tipo == self.SIMILARIDADES:
            print(self.matrizSimilaridades)
        else:
            print('Tipo incorreto!')
