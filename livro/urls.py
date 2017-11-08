from django.conf.urls import url

from .views import PesquisaView, SelecaoView, RecomendacaoView
#from . import views

app_name = 'livro'
urlpatterns = [
    url(r'pesquisa', PesquisaView.as_view(), name='pesquisa'),
    url(r'selecao', SelecaoView.as_view(), name='selecao'),
    url(r'recomendacao', RecomendacaoView.as_view(), name='recomendacao')
]
