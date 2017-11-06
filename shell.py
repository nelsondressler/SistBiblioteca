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

import math
import numpy as np

procLivros = ProcessamentoLivros('livros', 'livro.Livro')
procLivros.AtualizarDados()

if not procLivros.qtdTotalSimilaridades:
    if not procLivros.qtdTotalPesos:
        procLivros.CarregarMatrizFrequencias()
        procLivros.CarregarMatrizTF()
        procLivros.CarregarMatrizIDF()
        procLivros.CarregarMatrizTFIDF()
        procLivros.CarregarVetorMedias()
        procLivros.CarregarMatrizPesos()
        procLivros.CarregarPesosBD()
    else:
        procLivros.RecuperarMatrizPesos()
    procLivros.CarregarMatrizSimilaridades()
    procLivros.CarregarSimilaridadesBD()
else:
    procLivros.RecuperarMatrizSimilaridades()

#1a opção
idsLivrosJ = Similaridade.objects.filter(livro_i__id = id).order_by('-valor').values_list('livro_j__id', flat = True)[:n]

#2a opção
livrosJ = Livro.objects.filter(similaridade_livro_i__id = id).order_by('-similaridade__valor').values_list('similaridade_livro_j')[:n]

#Tipo de query
print(queryset.query)
print(Similaridade.objects.filter(livro_i_id = i).order_by('-valor').value_list('livro_j_id').query)
