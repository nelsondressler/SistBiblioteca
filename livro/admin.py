from django.contrib import admin

from .models import Livro
# Register your models here.
class LivroAdmin(admin.ModelAdmin):
    list_display = ['id', 'titulo', 'autor', 'editora', 'ano_publicacao'] # campos de apresentação
    list_display_links = ['id', 'titulo', 'autor', 'editora', 'ano_publicacao'] # campos habilitados para links 
    search_fields = ['titulo'] # campos de busca
    raw_id_fields = [] # campos de chave estrangeira (processamento de relacionamento)

    def get_ordering(self, request):
        return ['id']

admin.site.register(Livro, LivroAdmin)
