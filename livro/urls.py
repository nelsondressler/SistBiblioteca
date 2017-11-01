from django.conf.urls import url

from .views import PesquisaView

app_name = 'livro'
urlpatterns = [
    url(r'', PesquisaView.as_view(), name='pesquisa'),
]
