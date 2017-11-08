from django.conf.urls import url

from .views import PesquisaView, SelecaoView, RecomendacaoView

app_name = 'livro'
urlpatterns = [
    url(r'', PesquisaView.as_view(), name='pesquisa'),
    url(r'', SelecaoView.as_view(), name='pesquisa'),
    url(r'', RecomendacaoView.as_view(), name='pesquisa'),
]
