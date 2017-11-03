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

    class meta:
        indexes = [
            models.Index(fields = ['id'], name = 'usuario_index_1'),
            models.Index(fields = ['-id'], name = 'usuario_index_2'),
            models.Index(fields = ['nome'], name = 'usuario_index_3'),
            models.Index(fields = ['-nome'], name = 'usuario_index_4'),
            models.Index(fields = ['email'], name = 'usuario_index_5'),
            models.Index(fields = ['-email'], name = 'usuario_index_6'),
            models.Index(fields = ['login'], name = 'usuario_index_7'),
            models.Index(fields = ['-login'], name = 'usuario_index_8'),
            models.Index(fields = ['senha'], name = 'usuario_index_9'),
            models.Index(fields = ['-senha'], name = 'usuario_index_10'),
            models.Index(fields = ['cpf'], name = 'usuario_index_11'),
            models.Index(fields = ['-cpf'], name = 'usuario_index_12'),
            models.Index(fields = ['data_nascimento'], name = 'usuario_index_13'),
            models.Index(fields = ['-data_nascimento'], name = 'usuario_index_14')
        ]

class Pesquisa(models.Model):
    data = models.DateTimeField(auto_now = True)
    usuario = models.ForeignKey(Usuario, models.CASCADE)

    class meta:
        indexes = [
            models.Index(fields = ['id'], name = 'pesquisa_index_1'),
            models.Index(fields = ['-id'], name = 'pesquisa_index_2'),
            models.Index(fields = ['data'], name = 'pesquisa_index_3'),
            models.Index(fields = ['-data'], name = 'pesquisa_index_4'),
            models.Index(fields = ['usuario'], name = 'pesquisa_index_5'),
            models.Index(fields = ['-usuario'], name = 'pesquisa_index_6')
        ]

class PesquisaPalavraChave(models.Model):
    nome = models.CharField(max_length = 200)
    pesquisa = models.ForeignKey(Pesquisa, models.CASCADE)

    class meta:
        indexes = [
            models.Index(fields = ['id'], name = 'pesquisa_pc_index_1'),
            models.Index(fields = ['-id'], name = 'pesquisa_pc_index_2'),
            models.Index(fields = ['nome'], name = 'pesquisa_pc_index_3'),
            models.Index(fields = ['-nome'], name = 'pesquisa_pc_index_4'),
            models.Index(fields = ['pesquisa'], name = 'pesquisa_pc_index_5'),
            models.Index(fields = ['-pesquisa'], name = 'pesquisa_pc_index_6')
        ]

class PesquisaLivroSelecionado(models.Model):
    livro = models.ForeignKey(Livro, models.CASCADE)
    pesquisa = models.ForeignKey(Pesquisa, models.CASCADE)

    class meta:
        indexes = [
            models.Index(fields = ['id'], name = 'pesquisa_ls_index_1'),
            models.Index(fields = ['-id'], name = 'pesquisa_ls_index_2'),
            models.Index(fields = ['livro'], name = 'pesquisa_ls_index_3'),
            models.Index(fields = ['-livro'], name = 'pesquisa_ls_index_4'),
            models.Index(fields = ['pesquisa'], name = 'pesquisa_ls_index_5'),
            models.Index(fields = ['-pesquisa'], name = 'pesquisa_ls_index_6')
        ]

class PesquisaRecomendacao(models.Model):
    selecionado = models.ForeignKey(PesquisaLivroSelecionado, models.CASCADE)
    recomendado = models.ForeignKey(Livro, models.CASCADE, verbose_name='Livro recomendado')
    rating = models.BooleanField(default = True)
    data = models.DateTimeField(auto_now = True)

    class meta:
        indexes = [
            models.Index(fields = ['id'], name = 'pesquisa_r_index_1'),
            models.Index(fields = ['-id'], name = 'pesquisa_r_index_2'),
            models.Index(fields = ['selecionado'], name = 'pesquisa_r_index_3'),
            models.Index(fields = ['-selecionado'], name = 'pesquisa_r_index_4'),
            models.Index(fields = ['recomendado'], name = 'pesquisa_r_index_5'),
            models.Index(fields = ['-recomendado'], name = 'pesquisa_r_index_6'),
            models.Index(fields = ['rating'], name = 'pesquisa_r_index_7'),
            models.Index(fields = ['-rating'], name = 'pesquisa_r_index_8'),
            models.Index(fields = ['data'], name = 'pesquisa_r_index_9'),
            models.Index(fields = ['-data'], name = 'pesquisa_r_index_10'),
        ]
