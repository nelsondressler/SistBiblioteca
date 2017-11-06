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

#CREATE EXTENSION unaccent;
Livro.objects.filter(titulo__unaccent__contains = 'administracao')

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

valoresLivrosJ = Similaridade.objects.filter(livro_i__id = id).exclude(livro_j__id = id).order_by('-valor').values_list('valor', flat = True)[:n]
idsLivrosJ = Similaridade.objects.filter(livro_i__id = id).exclude(livro_j__id = id).order_by('-valor').values_list('livro_j__id', flat = True)[:n]
livrosJ = Livro.objects.filter(id__in = idsLivrosJ)

#Tipo de query
print(queryset.query)
print(Similaridade.objects.filter(livro_i_id = i).order_by('-valor').value_list('livro_j_id').query)
