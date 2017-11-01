from django.db import models

from termo.models import Termo

# Create your models here.
class Livro(models.Model):
    isbn = models.CharField(max_length = 13, unique = True)
    autor = models.CharField(max_length = 200)
    titulo = models.CharField(max_length = 500)
    descricao = models.TextField(null = True, blank = True)
    conteudo_processado = models.TextField(null = True, blank = True)
    editora = models.CharField(max_length = 200)
    ano_publicacao = models.PositiveIntegerField(null = True, blank = True)
    similaridades = models.ManyToManyField("self", through = "Similaridade", blank = True, symmetrical = False)
    termos = models.ManyToManyField(Termo, through = "Peso", blank = True, related_name = "termos")

    def __str__(self):
        return self.titulo

    class meta:
        managed = True

class Similaridade(models.Model):
    valor = models.FloatField()
    livro_i = models.ForeignKey(Livro, models.CASCADE, related_name = "livro_i")
    livro_j = models.ForeignKey(Livro, models.CASCADE, related_name = "livro_j")

    def __str__(self):
        return self.valor

    class meta:
        managed = True

class Peso(models.Model):
    valor = models.FloatField()
    termo = models.ForeignKey(Termo, models.CASCADE)
    livro = models.ForeignKey(Livro, models.CASCADE)

    def __str__(self):
        return self.valor

    class meta:
        managed = True
