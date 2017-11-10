from django.core.management.base import BaseCommand, CommandError

from usuario.models import Usuario

from usuario.libs import ProcessamentoUsuarios

class Command(BaseCommand):
    help = 'Sistema via linha de comando'

    def UsuarioExistente(self, username):
        qtdUsuarios = Usuario.objects.filter(username = username).count()

        if qtdUsuarios:
            return True

        return False

    def handle(self, *args, **options):
        resultado = False
        sair = False
        selecionado = False
        enviar = False
        avaliado = False
        explorado = False
        respostaInvalida = True

        while not sair:
            print('\n')
            print('SISTEMA DE RECOMENDAÇÃO PARA BIBLIOTECAS UNIVERSITÁRIAS')
            print('\n')

            print('Favor entrar com o seu login (#sair para sair do programa)')
            username = input('Login: ')

            if username == '#sair':
                sair = True
            else:
                if not self.UsuarioExistente(username):
                    print('Novo usuário! Favor entrar com os dados para cadastro (#sair para sair do programa)')
                    nome = input('Nome: ')
                    if nome == '#sair':
                        sair = True
                    else:
                        sobrenome = input('Sobrenome: ')
                        if sobrenome == '#sair':
                            sair = True
                        else:
                            email = input('E-mail: ')
                            if email == '#sair':
                                sair = True

                else:
                    nome = 'teste'
                    sobrenome = 'teste'
                    email = 'teste@teste.com'

                if not sair:
                    procUsuarios = ProcessamentoUsuarios(username = username, nome = nome, sobrenome = sobrenome, email = email)
                    logado = True

                    while logado:
                        while not resultado:
                            selecionado = False
                            print('\nO que deseja pesquisar? (#sair para sair da sua conta de usuário)')
                            textoPesquisado = input('Pesquisa: ')

                            if textoPesquisado == '#sair':
                                print('Entrei')
                                logado = False
                                resultado = True
                            else:
                                resultado = procUsuarios.PesquisarPalavraChave(textoPesquisado = textoPesquisado)

                                if resultado:
                                    while not selecionado:
                                        resposta = input('\nDeseja selecionar algum livro? (s/n): ')
                                        if resposta == 's':
                                            ids = input('Entre com os IDs dos livros que deseja selecionar (separados por vírgula): ')
                                            ids = list(ids.replace(' ','').split(','))
                                            ids = [int(elemento) for elemento in ids]
                                            selecionado = procUsuarios.SelecionarLivros(ids = ids)

                                            if selecionado:
                                                respostaInvalida = True
                                                resposta = input('\nDeseja enviar a lista de livros selecionados para recomendação? (s/n): ')
                                                while respostaInvalida:
                                                    if resposta == 's':
                                                        procUsuarios.EnviarLivrosSelecionados()

                                                        while not explorado:
                                                            resposta = input('\nDeseja explorar algum dos livros recomendados? (s/n): ')
                                                            if resposta == 's':
                                                                id = input('Entre com o ID do livro a ser explorado: ')
                                                                id = int(id)
                                                                procUsuarios.ExplorarLivro(id = id)
                                                            elif resposta == 'n':
                                                                explorado = True

                                                                while not avaliado:
                                                                    print('\nFavor avaliar cada um dos livros recomendados (1 para gostei e 0 para não gostei, separados por vírgula) por ordem de recomendação')
                                                                    ratings = input('Avaliações: ')
                                                                    ratings = list(ratings.replace(' ','').split(','))
                                                                    ratings = [int(elemento) for elemento in ratings]
                                                                    avaliado = procUsuarios.EnviarRatings(ratings = ratings)

                                                            else:
                                                                print('Resposta inválida!')
                                                    elif resposta == 'n':
                                                        respostaInvalida = False
                                                    else:
                                                        print('Resposta inválida!')
                                                        respostaInvalida = True
                                        elif resposta == 'n':
                                            selecionado = True
                                        else:
                                            print('Resposta inválida!')

                                    resultado = False

            if sair:
                print('\n')
                print('FIM!!!')
                print('\n')
