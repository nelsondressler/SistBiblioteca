from django.db import models

# Create your models here.
class Termo(models.Model):
    nome = models.CharField(max_length=200)

    def __str__(self):
        return self.nome

    class meta:
        indexes = [
            models.Index(fields = ['id'], name = 'termo_index_1'),
            models.Index(fields = ['-id'], name = 'termo_index_2'),
            models.Index(fields = ['nome'], name = 'termo_index_3'),
            models.Index(fields = ['-nome'], name = 'termo_index_4')
        ]
