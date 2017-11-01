import django
import sys
import os

sys.path.append('C:\\Users\\Nelson\\Documents\\SistBiblioteca\\bibinterativa')
os.environ['DJANGO_SETTINGS.MODULE'] = 'bibinterativa.settings'
django.setup()

from livro.libs import ProcessamentoLivros

from livro.models import Livro, Peso, Similaridade
from termo.models import Termo

import numpy as np

procL = ProcessamentoLivros('livros', 'livro.Livro')
procL.AtualizarDados()

procL.CarregarIdsLivroTermosMatrizesMN()

procL.CarregarMatrizFrequencias()
procL.CarregarMatrizTF()
procL.CarregarMatrizIDF()
procL.CarregarMatrizTFIDF()
procL.CarregarVetorMedias()
procL.CarregarMatrizPesos()
procL.CarregarPesosBD()

procL.CarregarIdsLivrosMatrizesMM()

procL.CarregarMatrizSimilaridades()
procL.CarregarSimilaridadesBD()


termoIds = Termo.objects.order_by('id').values_list('id', flat = True)
livroIds = Livro.objects.order_by('id').values_list('id', flat = True)
procL.idsLivroTermos.append((livroIds, termoIds))
print(ids)


id = idLivroI
n = quantElementos

#1a opção
idsLivrosJ = Similaridade.objects.filter(livro_i__id = id).order_by('-valor').value_list('livro_j__id')[:n]

#2a opção
livrosJ = Livro.objects.filter(similaridade_livro_i__id = id).order_by('-similaridade__valor').value_list('similaridade_livro_j')[:n]

#Tipo de query
print(queryset.query)
print(Similaridade.objects.filter(livro_i_id = i).order_by('-valor').value_list('livro_j_id').query)
