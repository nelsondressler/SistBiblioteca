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
