import django
import sys
import os

sys.path.append('C:\\Users\\Nelson\\Documents\\SistBiblioteca\\bibinterativa')
os.environ['DJANGO_SETTINGS.MODULE'] = 'bibinterativa.settings'
django.setup()

from livro.libs import ProcessamentoLivros

from livro.models import Livro, Peso, Similaridade
from termo.models import Termo

from django.db.models import When, Case, F, IntegerField, FloatField

import numpy as np

procLivros = ProcessamentoLivros('livros', 'livro.Livro')
procLivros.AtualizarDados()

#procLivros.CarregarMatrizFrequencias()
#procLivros.CarregarMatrizTF()
#procLivros.CarregarMatrizIDF()
#procLivros.CarregarMatrizTFIDF()
#procLivros.CarregarVetorMedias()
#procLivros.CarregarMatrizPesos()
#procLivros.CarregarPesosBD()

procLivros.RecuperarMatrizPesos()
procLivros.CarregarMatrizSimilaridades()
procLivros.CarregarSimilaridadesBD()

procLivros.RecuperarMatrizSimilaridades()

#Opção 1: ineficiente
m = []
for idLivro in procLivros.livroIds:
    colunas = []
    for idTermo in procLivros.termoIds:
        try:
            colunas.append(Peso.objects.filter(livro__id = idLivro, termo__id = idTermo)[0].valor)
        except:
            colunas.append(0)
    print('[Pesos] Livro ' + str(idLivro) + ' carregado.')
    m.append(colunas)

idLivro = procLivros.livroIds[0]
Termo.objects.order_by('id').annotate(pesoij = Case(When(peso__livro_id = idLivro, then = 'peso__valor'), default = 0, output_field = FloatField())).values_list('pesoij', flat = True)

#Opção 2: eficiente
m = []
for idLivro in procLivros.livroIds:
    m.append(Termo.objects.order_by('id').annotate(pesoij = Case(When(peso__livro_id = idLivro, then = 'peso__valor'), default = 0, output_field = FloatField())).values_list('pesoij', flat = True))

m = np.matrix(m)

idLivro = procLivros.livroIds[1]
colunas = []
for j, idTermo in enumerate(procLivros.termoIds):
    valor = Peso.objects.filter(livro__id = idLivro, termo__id = idTermo)
    if valor:
        colunas.append(float(str(valor[0])))
    else:
        colunas.append(0)

id = idLivroI
n = quantElementos

#1a opção
idsLivrosJ = Similaridade.objects.filter(livro_i__id = id).order_by('-valor').value_list('livro_j__id')[:n]

#2a opção
livrosJ = Livro.objects.filter(similaridade_livro_i__id = id).order_by('-similaridade__valor').value_list('similaridade_livro_j')[:n]

#Tipo de query
print(queryset.query)
print(Similaridade.objects.filter(livro_i_id = i).order_by('-valor').value_list('livro_j_id').query)
