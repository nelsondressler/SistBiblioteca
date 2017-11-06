from django.core.management.base import BaseCommand, CommandError
from livro.libs import ProcessamentoLivros

class Command(BaseCommand):
    help = 'Carrega todos os dados para o BD e executa todo o processamento necessário'

    def handle(self, *args, **options):
        print('\n')
        print('Gerando o arquivo .json...')
        procLivros = ProcessamentoLivros('livros', 'livro.Livro')
        procLivros.GerarArquivoJSON()
        self.stdout.write(self.style.SUCCESS('Arquivo gerado com sucesso.'))

        print('\n')
        print('Carregando o arquivo .json com os dados dos livros para o BD...')
        procLivros.CarregarFixtures()
        self.stdout.write(self.style.SUCCESS('Livros carregados com sucesso.'))

        print('\n')
        print('Gerando e carregando os stopwords para o BD...')
        procLivros.CarregarStopWords()
        self.stdout.write(self.style.SUCCESS('Stopwords carregadas com sucesso.'))

        print('\n')
        print('Gerando e carregando os documentos (conteudo_processado) e termos para o BD...')
        procLivros.CarregarTermos()
        self.stdout.write(self.style.SUCCESS('Documentos e termos carregados com sucesso.'))

        print('\n')
        print('Atualizando os dados de quantidades e ids de documentos e termos (M x N)...')
        procLivros.AtualizarDados()
        self.stdout.write(self.style.SUCCESS('Ids gerados com sucesso.'))


        if not procLivros.qtdTotalSimilaridades:

            if not procLivros.qtdTotalPesos:
                print('\n')
                print('Calculando as frequências dos termos em cada documento e gerando uma matriz...')
                procLivros.CarregarMatrizFrequencias()
                self.stdout.write(self.style.SUCCESS('Matriz gerada com sucesso.'))

                print('\n')
                print('Calculando os TFs dos termos em cada documento e gerando uma matriz...')
                procLivros.CarregarMatrizTF()
                self.stdout.write(self.style.SUCCESS('Matriz gerada com sucesso.'))

                print('\n')
                print('Calculando os IDFs dos termos em cada documento e gerando uma matriz...')
                procLivros.CarregarMatrizIDF()
                self.stdout.write(self.style.SUCCESS('Matriz gerada com sucesso.'))

                print('\n')
                print('Calculando os TF-IDFs dos termos em cada documento e gerando uma matriz...')
                procLivros.CarregarMatrizTFIDF()
                self.stdout.write(self.style.SUCCESS('Matriz gerada com sucesso.'))

                print('\n')
                print('Calculando as médias dos termos em cada documento e gerando uma matriz...')
                procLivros.CarregarVetorMedias()
                self.stdout.write(self.style.SUCCESS('Matriz gerada com sucesso.'))

                print('\n')
                print('Calculando os pesos dos termos em cada documento e gerando uma matriz...')
                procLivros.CarregarMatrizPesos()
                self.stdout.write(self.style.SUCCESS('Matriz gerada com sucesso.'))

                print('\n')
                print('Carregando os pesos para o BD...')
                procLivros.CarregarPesosBD()
                self.stdout.write(self.style.SUCCESS('Pesos carregados com sucesso.'))

            else:
                print('\n')
                print('Recuperando os pesos existentes no BD e gerando uma matriz...')
                procLivros.RecuperarMatrizPesos()
                self.stdout.write(self.style.SUCCESS('Matriz gerada com sucesso.'))


            print('\n')
            print('Calculando as similaridades entre os documentos e gerando uma matriz...')
            procLivros.CarregarMatrizSimilaridades()
            self.stdout.write(self.style.SUCCESS('Matriz gerada com sucesso.'))

            print('\n')
            print('Carregando as similaridades para o BD...')
            procLivros.CarregarSimilaridadesBD()
            self.stdout.write(self.style.SUCCESS('Similaridades carregadas com sucesso.'))

        else:
            print('\n')
            print('Recuperando os pesos existentes no BD e gerando uma matriz...')
            procLivros.RecuperarMatrizSimilaridades()
            self.stdout.write(self.style.SUCCESS('Matriz gerada com sucesso.'))
