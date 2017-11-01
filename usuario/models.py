from django.db import models

from livro.models import Livro

# Create your models here.
class Usuario(models.Model):
    nome = models.CharField(max_length = 200)
    email = models.EmailField()
    login = models.CharField(max_length = 50)
    senha = models.CharField(max_length = 50)
    cpf = models.CharField(max_length = 13)
    data_nascimento = models.DateField(null = True, blank = True)

    def __str__(self):
        return self.nome

class PesquisaPalavraChave(models.Model):
    nome = models.CharField(max_length = 200)
    pesquisa = models.ForeignKey(Pesquisa, models.CASCADE)

class Pesquisa(models.Model):
    data = models.DateTimeField(auto_now = True)
    usuario = models.ForeignKey(Usuario, models.CASCADE)
    livro = models.ForeignKey(Livro, models.CASCADE)

class Recomendacao(models.Model):
    rating = models.BooleanField(default = True)
    data = models.DateTimeField(auto_now = True)
    usuario = models.ForeignKey(Usuario, models.CASCADE)
    livro = models.ForeignKey(Livro, models.CASCADE)
