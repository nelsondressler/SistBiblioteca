from django.core.management.base import BaseCommand, CommandError

from usuario.models import Usuario

from usuario.libs import ProcessamentoUsuarios as pu

class Command(BaseCommand):
    help = 'Sistema de recomendação via linha de comando'

    def ReinicializarEstados(self):
        self.resultado = False
        self.sair = False
        self.selecionado = False
        self.enviar = False
        self.avaliado = False
        self.explorado = False
        self.respostaInvalida = True

    def handle(self, *args, **options):
        self.ReinicializarEstados()

        print('\n')
        print('SISTEMA DE RECOMENDAÇÃO PARA BIBLIOTECAS UNIVERSITÁRIAS')
        print('\n')

        while not self.sair:
            print('\nFavor entrar com o seu login (#sair para sair do programa)')
            username = input('Login: ')

            if username == '#sair':
                self.sair = True
            elif not username:
                print('[Erro] Favor entrar com um login válido')
                self.sair = False
            else:
                if not pu.UsuarioExistente(pu, username):
                    print('Novo usuário! Favor entrar com os dados para cadastro (#sair para sair do programa)')
                    nome = input('Nome: ')
                    if nome == '#sair':
                        self.sair = True
                    else:
                        sobrenome = input('Sobrenome: ')
                        if sobrenome == '#sair':
                            self.sair = True
                        else:
                            email = input('E-mail: ')
                            if email == '#sair':
                                self.sair = True

                else:
                    nome = 'teste'
                    sobrenome = 'teste'
                    email = 'teste@teste.com'

                if not self.sair:
                    procUsuarios = pu(username = username, nome = nome, sobrenome = sobrenome, email = email)
                    self.logado = True

                    while self.logado:
                        self.ReinicializarEstados()

                        while not self.resultado:
                            self.selecionado = False
                            print('\nO que deseja pesquisar? (#sair para sair da sua conta de usuário)')
                            textoPesquisado = input('Pesquisa: ')

                            if textoPesquisado == '#sair':
                                self.logado = False
                                self.resultado = True
                            elif not textoPesquisado:
                                print('[Erro] Entre com algum texto')
                            else:
                                self.resultado = procUsuarios.PesquisarPalavraChave(textoPesquisado = textoPesquisado)

                                if self.resultado:
                                    while not self.selecionado:
                                        resposta = input('\nDeseja selecionar algum livro? (s/n): ')
                                        if resposta == 's':
                                            ids = input('Entre com os IDs dos livros que deseja selecionar (separados por vírgula): ')

                                            try:
                                                ids = list(ids.replace(' ','').split(','))
                                                ids = [int(elemento) for elemento in ids]
                                                self.selecionado = procUsuarios.SelecionarLivros(ids = ids)
                                            except:
                                                print('Resposta inválida!')

                                            if self.selecionado:
                                                self.respostaInvalida = True
                                                resposta = input('\nDeseja enviar a lista de livros selecionados para recomendação? (s/n): ')
                                                while self.respostaInvalida:
                                                    if resposta == 's':
                                                        procUsuarios.EnviarLivrosSelecionados()

                                                        while not self.explorado:
                                                            resposta = input('\nDeseja explorar algum dos livros recomendados? (s/n): ')
                                                            if resposta == 's':
                                                                id = input('Entre com o ID do livro a ser explorado: ')

                                                                try:
                                                                    id = int(id)
                                                                    procUsuarios.ExplorarLivro(id = id)
                                                                except:
                                                                    print('Resposta inválida!')
                                                            elif resposta == 'n':
                                                                self.explorado = True

                                                                while not self.avaliado:
                                                                    print('\nFavor avaliar cada um dos livros recomendados (1 para gostei e 0 para não gostei, separados por vírgula) por ordem de recomendação')
                                                                    print('OBS: A sua avaliação deve ser feita com base no livro selecionado, ou seja, se as respectivas recomendações estavam relacionadas ao livro selecionado (1) ou não (0).')
                                                                    ratings = input('Avaliações: ')
                                                                    try:
                                                                        if not ratings:
                                                                            print('A avaliação foi recebida como positiva para todos os livros recomendados.\n')
                                                                            self.avaliado = True
                                                                        else:
                                                                            ratings = list(ratings.replace(' ','').split(','))
                                                                            ratings = [int(elemento) for elemento in ratings]

                                                                            self.avaliado = procUsuarios.EnviarRatings(ratings = ratings)
                                                                    except:
                                                                        print('\nResposta inválida.\n')

                                                            else:
                                                                print('Resposta inválida!')
                                                    elif resposta == 'n':
                                                        self.respostaInvalida = False
                                                    else:
                                                        print('Resposta inválida!')
                                                        self.respostaInvalida = True
                                        elif resposta == 'n':
                                            self.selecionado = True
                                        else:
                                            print('Resposta inválida!')

        print('\n')
        print('FIM!!!')
        print('\n')
