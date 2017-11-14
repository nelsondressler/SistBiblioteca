import django
import sys
import os

sys.path.append('C:\\Users\\Nelson\\Documents\\SistBiblioteca\\bibinterativa')
os.environ['DJANGO_SETTINGS.MODULE'] = 'bibinterativa.settings'
django.setup()

#------------------------------------- PROCESSAMENTO DOS LIVROS -------------------------------------

from livro.libs import ProcessamentoLivros

procLivros = ProcessamentoLivros('livros', 'livro.Livro')
procLivros.ProcessarDados()

#------------------------------------- SISTEMA USUÁRIO FINAL -------------------------------------

from usuario.libs import ProcessamentoUsuarios

#(1) Novo Usuário (username único)
procUsuarios = ProcessamentoUsuarios(username = '', nome = '', sobrenome = '', email = '')

#(2) Nova Pesquisa
procUsuarios.PesquisarPalavraChave(textoPesquisado = '')

#(3) Manipular lista de Livros Selecionados (incluir, excluir, limpar)
procUsuarios.SelecionarLivros(ids = []) #lista inteira dos ids da pesquisa selecionados pelo usuário
procUsuarios.DesmarcarLivros(ids = [])
procUsuarios.LimparSelecao()

#(4) Nova Pesquisa?
#voltar ao passo (2)

#(5.1) Enviar Livros Selecionados e Receber os Livros Recomendados
procUsuarios.EnviarLivrosSelecionados()

#(5.2) Detalhes dos Livros
procUsuarios.ExplorarLivro(id = )

#(6) Enviar Avaliação
procUsuarios.EnviarRatings(ratings = []) #lista inteira dos ratings pra cada livro recomendado ao usuário


from livro.models import Livro, Peso, Similaridade
from termo.models import Termo
from stopword.models import Stopword
from usuario.models import Usuario, Pesquisa, PesquisaPalavraChave, PesquisaLivroSelecionado, PesquisaRecomendacao

Usuario.objects.count()

avaliacoes = []
idsSelecionados = PesquisaLivroSelecionado.objects.order_by('livro__id').values_list('livro__id', flat = True)
for idSelecionado in idsSelecionados:
    likesSelecionadoRecomendado = PesquisaRecomendacao.objects.filter(selecionado__livro__id = idSelecionado, rating = 1).count()
    dislikesSelecionadoRecomendado = PesquisaRecomendacao.objects.filter(selecionado__livro__id = idSelecionado, rating = 0).count()
    avaliacoes.append((idSelecionado, [likesSelecionadoRecomendado, dislikesSelecionadoRecomendado]))

for idSelecionado, ratings in avaliacoes:
    livro = Livro.objects.get(id = idSelecionado)
    likes = ratings[0]
    dislikes = ratings[1]
    print('[' + str(idSelecionado) + '] ' + livro.titulo + ':')
    print('likes = ' + str(likes) + '; dislikes = ' + str(dislikes))

likesTotal = PesquisaRecomendacao.objects.filter(rating = 1).count()
dislikesTotal = PesquisaRecomendacao.objects.filter(rating = 0).count()
