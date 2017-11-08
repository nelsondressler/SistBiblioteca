from django.db import models

from django.utils.timezone import now

from django.contrib.auth.models import AbstractUser
#from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin, BaseUserManager)

from livro.models import Livro

from .managers import UserManager

# Create your models here.
class Usuario(AbstractUser):
    username = models.CharField(unique = True, max_length = 50)
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    email = models.EmailField(unique = True, max_length = 50)
    is_verified = models.BooleanField(default = False)
    is_staff = models.BooleanField(default = False)
    is_active = models.BooleanField(default = False)
    date_joined = models.DateTimeField(default = now)

    #objects = BaseUserManager()
    objects = UserManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

    class meta:
        indexes = [

        ]
Usuario.groups.related_name = 'user_group'

class Pesquisa(models.Model):
    data = models.DateTimeField(default = now)
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
    data = models.DateTimeField(default = now)

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
