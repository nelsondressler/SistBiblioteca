import sys
import os
import re

import csv
import codecs
import json
from stop_words import get_stop_words

from django.core.management import call_command
from django.db.models import When, Case, F, IntegerField
from django.utils.text import slugify

from livro.models import Livro, Peso, Similaridade
from termo.models import Termo
from stopword.models import Stopword

from apiclient.discovery import build
from googleapiclient.errors import HttpError

import math
import numpy as np

class ProcessamentoLivros:
    MxN, MxM, LivrosM, TermosN, Frequencias, TFs, IDFs, TFIDFs, Medias, Pesos, Similaridades = range(9)

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

        self.idsLivroTermos = []
        self.idsLivrosIJ = []

        self.medias = []
        self.matrizFrequencias = []
        self.matrizTF = []
        self.matrizIDF = []
        self.matrizTFIDF = []
        self.matrizPesos = []
        self.matrizSimilaridades = []

    def AtualizarDados(self):
        self.qtdTotalDocs = Livro.objects.count()
        self.qtdTotalTermos = Termo.objects.count()

        self.termoIds = Termo.objects.order_by('id').values_list('id', flat = True)
        self.livroIds = Livro.objects.order_by('id').values_list('id', flat = True)

        self.CarregarIdsLivroTermosMatrizesMN()
        self.CarregarIdsLivrosMatrizesMM()

    def ConsultarDescricao(self, isbn):
        #chaveApiGoogle = 'AIzaSyDzGpl0S6cQi8uxtb8Q3aEX56k7gsDO6K4' #nelsondr58@gmail.com
        chaveApiGoogle = 'AIzaSyBDKZQ92tqsD4CvadBJpP0ns3NVZQwkZUw' #bi@escritapen.com.br
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
            palavras = [elemento for elemento in palavras if elemento not in stopwords]

            livro.conteudo_processado = ' '.join(palavras)
            livro.save()

            for p in palavras:
                p = p.strip()

                Termo.objects.get_or_create(nome = p)

        self.AtualizarDados()

    def CarregarIdsLivroTermosMatrizesMN(self):
        for id in self.livroIds:
            self.idsLivroTermos.append((id, self.termoIds))

    def CarregarMatrizFrequencias(self):
        termos = Termo.objects.order_by('id')

        mF = []

        for documento, id in Livro.objects.order_by('id').values_list('conteudo_processado', 'id'):
            palavras = documento.split(" ")

            colunas = []
            for termo in termos:
                frequencia = 0

                for p in palavras:
                    #Normaliza para minuscula para comparar case insensitive
                    if termo.nome.lower() == p.lower():
                        frequencia += 1

                colunas.append(frequencia)
                #print('F(' + str(id) + ',' + str(termo.id) + ') = ' + str(frequencia))

            mF.append(colunas)
            print('[Frequencias] Livro ' + str(id) + ' calculado.')

        self.matrizFrequencias = np.matrix(mF) #Matriz do numpy

    def CarregarMatrizTF(self):
        termos = Termo.objects.order_by('id')

        mTF = []

        for i, (documento, id) in enumerate(Livro.objects.order_by('id').values_list('conteudo_processado', 'id')):
            palavras = documento.split(" ")
            qtdTermosEmDoc = len(palavras)

            colunas = []

            for j, termo in enumerate(termos):
                tf = self.matrizFrequencias[i,j] / qtdTermosEmDoc

                colunas.append(tf)
                #print('TF(' + str(id) + ',' + str(termo.id) + ') = ' + str(tf))

            #Gravando as linhas (conjunto de colunos) na matriz de TF
            mTF.append(colunas)
            print('[TFs] Livro ' + str(id) + ' calculado.')

        self.matrizTF = np.matrix(mTF) #Matriz do numpy

    def CarregarMatrizIDF(self):
        termos = Termo.objects.order_by('id')

        mIDF = []

        for documento, id in Livro.objects.order_by('id').values_list('conteudo_processado', 'id'):
            palavras = documento.split(" ")
            qtdTermosEmDoc = len(palavras)

            colunas = []

            for termo in termos:
                qtdDocsComTermo = Livro.objects.filter(conteudo_processado__icontains = termo).count()

                idf = math.log10(self.qtdTotalDocs / qtdDocsComTermo)

                colunas.append(idf)
                #print('IDF(' + str(id) + ',' + str(termo.id) + ') = ' + str(idf))

            #Gravando as linhas (conjunto de colunos) na matriz de TF
            mIDF.append(colunas)
            print('[IDFs] Livro ' + str(id) + ' calculado.')

        self.matrizIDF = np.matrix(mIDF) #Matriz do numpy

    def CarregarMatrizTFIDF(self):
        self.matrizTFIDF = np.multiply(self.matrizTF, self.matrizIDF)
        print('[TFIDFs] Livros calculado(s):\n' + str(livroIds))

    def CarregarVetorMedias(self):
        vM = []
        med = 0

        for i, ci in enumerate(self.matrizTFIDF):
            for j, cj in enumerate(ci):
                med = med + cj ** 2

            med = math.sqrt(med)
            vM.append(med)
            #print('M(' + str(idsLivroTermos[i]) + ') = ' + str(med))
            print('[Médias] Livro ' + str(idsLivroTermos[i]) + ' calculado.')

        self.medias = np.array(vM)

    def CarregarMatrizPesos(self):
        mP = []

        for i, ci in enumerate(self.matrizTFIDF):
            colunas = []

            for j, cj in enumerate(ci):
                peso = cj / self.medias[i]
                colunas.append(peso)
                #print('W(' + str(id) + ',' + str(termo.id) + ') = ' + str(peso))

            mP.append(colunas)
            print('[Pesos] Livro ' + str(id) + ' calculado.')

        self.matrizPesos = np.matrix(mP) #Matriz do numpy

    def CarregarPesosBD(self):
        for i, ci in enumerate(self.matrizPesos):
            idLivro, termos = idsLivroTermos[i]
            for j, cj in enumerate(ci):
                idTermo = termos[j]
                if cj:
                    try:
                        peso = Peso.objects.get(termo__id = idTermo, livro__id = idLivro)
                        peso.valor = cj
                        peso.save()

                    except Peso.DoesNotExist:
                        Peso.objects.create(termo__id = idTermo, livro__id = idLivro, valor = cj)

    def ProcessarPesos(self):
        #(1) Valores de totais, IDs MxN, IDs MxM
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

        for livroId in Livro.objects.order_by('id').values_list('id', flat = True):
            m.append(
                Termo.objects.order_by('id').annotate(peso = Case(When(peso__livro__id = livroId, then = F('peso__valor')), When(peso__livro__isnull = True, then = 0), output_field = IntegerField())).values_list('peso', flat = True))

        m = np.matrix(m)
        return m

    def CarregarIdsLivrosMatrizesMM(self):
        for i, idLivroI in enumerate(self.livroIds):
            idsLivrosJ = []
            for j, idLivroJ in enumerate(self.livroIds):
                idsLivrosJ.append(idLivroJ)
            self.idsLivrosIJ.append((idLivroI, idsLivrosJ))

    def CarregarMatrizSimilaridades(self):
        mSimilaridades = []

        for i in range(0, qtdTotalDocs):
            idLivroI, termos = self.idsLivroTermos[i]
            livroI = Livro.objects.get(id = idLivroI)

            colunas = []
            idsLivrosJ = []
            for j in range(0, qtdTotalDocs):
                idLivroJ, termos = self.idsLivroTermos[j]
                livroJ = Livro.objects.get(id = idLivroJ)

                #Acumulando os somatórios de D(i,j), D(i) e D(j)
                somatorioDiDj = np.sum(np.multiply(matrizPesos[i], matrizPesos[j]))
                somatorioDi = np.sum(np.power(matrizPesos[i], 2))
                somatorioDj = np.sum(np.power(matrizPesos[j], 2))

                #Calculando a similaridade de D(i,j)
                similaridadeIJ = somatorioDiDj / math.sqrt(somatorioDi, somatorioDj)

                colunas.append(similaridadeIJ)
                idsLivrosJ.append(idLivroJ)

            mSimilaridades.append(colunas)

        self.matrizSimilaridades = np.matrix(mSimilaridades)

    def CarregarSimilaridadesBD(self):
        for i, ci in enumerate(self.matrizSimilaridades):
            idLivroI, idsLivrosJ = self.idsLivrosIJ[i]
            for j, cj in enumerate(ci):
                idLivroJ = idsLivrosJ[j]
                if cj:
                    try:
                        similaridade = Similaridade.objects.get(livro_i = idLivroI, livro_j = idLivroJ)
                        similaridade.valor = cj
                        similaridade.save()
                    except Similaridade.DoesNotExist:
                        Similaridade.objects.create(livro_i = idLivroI, livro_j = idLivroJ, valor = cj)

    def ProcessarSimilaridades(self):
        #(1) Valores de totais, IDs MxN, IDs MxM
        self.AtualizarDados()

        #(2) Matriz de Similaridades
        self.CarregarMatrizSimilaridades()

        #(6) Similaridades -> BD
        self.CarregarSimilaridadesBD()

    def RecuperarMatrizSimilaridades(self):
        m = []

        for livroId in Livro.objects.order_by('id').values_list('id', flat = True):
            m.append(
                Livro.objects.order_by('id').annotate(total = Case(When(similaridade__livro__id = livroId, then = F('peso__valor')), When(similaridade__livro__isnull = True, then = 0), output_field = IntegerField())).values_list('total', flat = True))

        m = np.matrix(m)
        return m

    def CalcularIdsLivrosMaisProximos(self, id, qtde):
        ids = Similaridade.objects.filter(livro_i__id = id).order_by('-valor').value_list('livro_j__id')[:n]
        return ids

    def CalcularLivrosMaisProximos(self, id, qtde):
        livros = = Livro.objects.filter(similaridade_livro_i__id = id).order_by('-similaridade__valor').value_list('similaridade_livro_j')[:n]
        return livros

    def ExibirIds(self, tipo):
        #Tipos: MxN, MxM, LivrosM, TermosN
        if tipo == self.MxN:
            print(self.idsLivroTermos)
        elif tipo == self.MxM:
            print(self.idsLivrosIJ)
        elif tipo == self.TermosN:
            print(self.livroIds)
        elif tipo == self.LivrosM:
            print(self.termoIds)
        else:
            print('Tipo incorreto!')

    def ExibirVetor(self, tipo):
        #Tipos: Medias
        if tipo == self.Medias:
            print(self.medias)
        else:
            print('Tipo incorreto!')

    def ExibirMatriz(self, tipo):
        #Tipos: Frequencias, TFs, IDFs, TFIDFs, Pesos, Similaridades
        if tipo == self.Frequencias:
            print(self.matrizFrequencias)
        elif tipo == self.TFs:
            print(self.matrizTF)
        elif tipo == self.IDfs:
            print(self.matrizIDF)
        elif tipo == self.TFIDFs:
            print(self.matrizTFIDF)
        elif tipo == self.Pesos:
            print(self.matrizPesos)
        elif tipo == self.Similaridades:
            print(self.matrizSimilaridades)
        else:
            print('Tipo incorreto!')
