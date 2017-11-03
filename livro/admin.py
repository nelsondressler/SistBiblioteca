from django.contrib import admin

from .models import Livro, Peso, Similaridade

# Register your models here.
class LivroAdmin(admin.ModelAdmin):
    list_display = ['id', 'titulo', 'autor', 'editora', 'ano_publicacao'] # campos de apresentação
    list_display_links = ['id', 'titulo', 'autor', 'editora', 'ano_publicacao'] # campos habilitados para links
    search_fields = ['titulo'] # campos de busca
    raw_id_fields = [] # campos de chave estrangeira (processamento de relacionamento)

    def get_ordering(self, request):
        return ['id']

class PesoAdmin(admin.ModelAdmin):
    list_display = ['id', 'livro', 'termo', 'valor'] # campos de apresentação
    list_display_links = ['id', 'livro', 'termo', 'valor'] # campos habilitados para links
    search_fields = ['livro', 'termo'] # campos de busca
    raw_id_fields = [] # campos de chave estrangeira (processamento de relacionamento)

    def get_ordering(self, request):
        return ['id']

class SimilaridadeAdmin(admin.ModelAdmin):
    list_display = ['id', 'livro_i', 'livro_j', 'valor'] # campos de apresentação
    list_display_links = ['id', 'livro_i', 'livro_j', 'valor'] # campos habilitados para links
    search_fields = ['livro_i', 'livro_j'] # campos de busca
    raw_id_fields = [] # campos de chave estrangeira (processamento de relacionamento)

    def get_ordering(self, request):
        return ['id']

admin.site.register(Livro, LivroAdmin)
admin.site.register(Peso, PesoAdmin)
admin.site.register(Similaridade, SimilaridadeAdmin)
