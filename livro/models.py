from django.db import models
from django.contrib.postgres.search import SearchVector

from termo.models import Termo

# Create your models here.
class Livro(models.Model):
    isbn = models.CharField(max_length = 13, unique = True)
    autor = models.CharField(max_length = 200)
    titulo = models.CharField(max_length = 500)
    descricao = models.TextField(null = True, blank = True)
    descricao_vector = SearchVector(null = True, blank = True)
    conteudo_processado = models.TextField(null = True, blank = True)
    conteudo_processado_vector = SearchVector(null = True, blank = True)
    editora = models.CharField(max_length = 200)
    ano_publicacao = models.PositiveIntegerField(null = True, blank = True)
    similaridades = models.ManyToManyField("self", through = "Similaridade", blank = True, symmetrical = False)
    termos = models.ManyToManyField(Termo, through = "Peso", blank = True, related_name = "termos")

    def get_similares(self):
        pass

    def __str__(self):
        return self.titulo

    class meta:
        managed = True
        indexes = [
            models.Index(fields = ['id'], name = 'livro_index_1'),
            models.Index(fields = ['-id'], name = 'livro_index_2'),
            models.Index(fields = ['isbn'], name = 'livro_index_3'),
            models.Index(fields = ['-isbn'], name = 'livro_index_4'),
            models.Index(fields = ['autor'], name = 'livro_index_5'),
            models.Index(fields = ['-autor'], name = 'livro_index_6'),
            models.Index(fields = ['titulo'], name = 'livro_index_7'),
            models.Index(fields = ['-titulo'], name = 'livro_index_8'),
            models.Index(fields = ['editora'], name = 'livro_index_9'),
            models.Index(fields = ['-editora'], name = 'livro_index_10'),
            models.Index(fields = ['ano_publicacao'], name = 'livro_index_11'),
            models.Index(fields = ['-ano_publicacao'], name = 'livro_index_12')
        ]

class Peso(models.Model):
    valor = models.FloatField()
    termo = models.ForeignKey(Termo, models.CASCADE)
    livro = models.ForeignKey(Livro, models.CASCADE)

    def __str__(self):
        return str(self.valor)

    class meta:
        managed = True
        indexes = [
            models.Index(fields = ['id'], name = 'peso_index_1'),
            models.Index(fields = ['-id'], name = 'peso_index_2'),
            models.Index(fields = ['valor'], name = 'peso_index_3'),
            models.Index(fields = ['-valor'], name = 'peso_index_4'),
            models.Index(fields = ['termo'], name = 'peso_index_5'),
            models.Index(fields = ['-termo'], name = 'peso_index_6'),
            models.Index(fields = ['livro'], name = 'peso_index_7'),
            models.Index(fields = ['-livro'], name = 'peso_index_8')
        ]

class Similaridade(models.Model):
    valor = models.FloatField()
    livro_i = models.ForeignKey(Livro, models.CASCADE, related_name = "livro_i")
    livro_j = models.ForeignKey(Livro, models.CASCADE, related_name = "livro_j")

    def __str__(self):
        return str(self.valor)

    class meta:
        managed = True
        indexes = [
            models.Index(fields = ['id'], name = 'similaridade_index_1'),
            models.Index(fields = ['-id'], name = 'similaridade_index_2'),
            models.Index(fields = ['valor'], name = 'similaridade_index_3'),
            models.Index(fields = ['-valor'], name = 'similaridade_index_4'),
            models.Index(fields = ['livro_i'], name = 'similaridade_index_5'),
            models.Index(fields = ['-livro_i'], name = 'similaridade_index_6'),
            models.Index(fields = ['livro_j'], name = 'similaridade_index_7'),
            models.Index(fields = ['-livro_j'], name = 'similaridade_index_8')
        ]
