from django.views.generic import View
from django.shortcuts import render

from .models import Livro
from .forms import PesquisaForm, ResultadoForm

class PesquisaView(View):
    def get(self, request):
        if request.user.username == '':
            request.user.username = 'anônimo'

        pesquisa = PesquisaForm()
        return render(request, 'livro/index.html', {
            'livro_form': pesquisa,
            'username': request.user.username
        })

    def post(self, request):
        pesquisa = PesquisaForm(request.POST)

        if request.user.username == '':
            request.user.username = 'anônimo'

        if pesquisa.is_valid():
            livros = Livro.objects.filter(titulo__icontains = pesquisa.cleaned_data['titulo']).order_by('id')

            return render(request, 'livro/resultado.html', {
                'livro_form': pesquisa,
                'resultado_form': ResultadoForm(),
                'livros' : livros,
                'username': request.user.username
            })
        else:
            pass

class ResultadoView(View):
    pass
