from django.contrib import admin

from .models import Termo

# Register your models here.
class TermoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome'] # campos de apresentação
    list_display_links = ['id', 'nome'] # campos habilitados para links
    search_fields = ['nome'] # campos de busca
    raw_id_fields = [] # campos de chave estrangeira (processamento de relacionamento)

    def get_ordering(self, request):
        return ['id']

admin.site.register(Termo, TermoAdmin)
