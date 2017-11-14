from django.contrib import admin

from .models import Usuario, Pesquisa, PesquisaPalavraChave, PesquisaLivroSelecionado, PesquisaRecomendacao

# Register your models here.
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'first_name', 'last_name', 'email', 'is_verified', 'is_staff', 'is_active', 'date_joined'] # campos de apresentação
    list_display_links = ['id', 'username', 'first_name', 'last_name', 'email', 'is_verified', 'is_staff', 'is_active', 'date_joined'] # campos habilitados para links
    search_fields = ['username'] # campos de busca
    raw_id_fields = [] # campos de chave estrangeira (processamento de relacionamento)

    def get_ordering(self, request):
        return ['id']

class PesquisaAdmin(admin.ModelAdmin):
    list_display = ['id', 'data', 'usuario'] # campos de apresentação
    list_display_links = ['id', 'data', 'usuario'] # campos habilitados para links
    search_fields = ['usuario'] # campos de busca
    raw_id_fields = [] # campos de chave estrangeira (processamento de relacionamento)

    def get_ordering(self, request):
        return ['id']

class PesquisaPalavraChaveAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'pesquisa'] # campos de apresentação
    list_display_links = ['id', 'pesquisa', 'nome'] # campos habilitados para links
    search_fields = ['nome'] # campos de busca
    raw_id_fields = [] # campos de chave estrangeira (processamento de relacionamento)

    def get_ordering(self, request):
        return ['id']

class PesquisaLivroSelecionadoAdmin(admin.ModelAdmin):
    list_display = ['id', 'livro', 'pesquisa'] # campos de apresentação
    list_display_links = ['id', 'pesquisa', 'livro'] # campos habilitados para links
    search_fields = ['livro'] # campos de busca
    raw_id_fields = [] # campos de chave estrangeira (processamento de relacionamento)

    def get_ordering(self, request):
        return ['id']

class PesquisaRecomendacaoAdmin(admin.ModelAdmin):
    list_display = ['id', 'selecionado', 'recomendado', 'rating', 'data'] # campos de apresentação
    list_display_links = ['id', 'selecionado', 'recomendado', 'rating', 'data'] # campos habilitados para links
    search_fields = ['recomendado'] # campos de busca
    raw_id_fields = [] # campos de chave estrangeira (processamento de relacionamento)

    def get_ordering(self, request):
        return ['id']


admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Pesquisa, PesquisaAdmin)
admin.site.register(PesquisaPalavraChave, PesquisaPalavraChaveAdmin)
admin.site.register(PesquisaLivroSelecionado, PesquisaLivroSelecionadoAdmin)
admin.site.register(PesquisaRecomendacao, PesquisaRecomendacaoAdmin)
