from django.core.management.base import BaseCommand, CommandError
from livro.libs import ProcessamentoLivros

class Command(BaseCommand):
    help = 'Carrega todos os dados para o BD e executa todo o processamento necessário'

    def handle(self, *args, **options):
        print('\n')
        print('Gerando o arquivo .json...')
        procL = ProcessamentoLivros('livros', 'livro.Livro')
        procL.GerarArquivoJSON()
        self.stdout.write(self.style.SUCCESS('Arquivo gerado com sucesso.'))

        print('\n')
        print('Carregando o arquivo .json com os dados dos livros para o BD...')
        procL.CarregarFixtures()
        self.stdout.write(self.style.SUCCESS('Livros carregados com sucesso.'))

        print('\n')
        print('Gerando e carregando os stopwords para o BD...')
        procL.CarregarStopWords()
        self.stdout.write(self.style.SUCCESS('Stopwords carregadas com sucesso.'))

        print('\n')
        print('Gerando e carregando os documentos (conteudo_processado) e termos para o BD...')
        procL.CarregarTermos()
        self.stdout.write(self.style.SUCCESS('Documentos e termos carregados com sucesso.'))

        print('\n')
        print('Gerando os ids de documentos e termos (M x N)...')
        procL.CarregarIdsLivroTermosMatrizesMN()
        self.stdout.write(self.style.SUCCESS('Ids gerados com sucesso.'))

        print('\n')
        print('Calculando as frequências dos termos em cada documento e gerando uma matriz...')
        procL.CarregarMatrizFrequencias()
        self.stdout.write(self.style.SUCCESS('Matriz gerada com sucesso.'))

        print('\n')
        print('Calculando os TFs dos termos em cada documento e gerando uma matriz...')
        procL.CarregarMatrizTF()
        self.stdout.write(self.style.SUCCESS('Matriz gerada com sucesso.'))

        print('\n')
        print('Calculando os IDFs dos termos em cada documento e gerando uma matriz...')
        procL.CarregarMatrizIDF()
        self.stdout.write(self.style.SUCCESS('Matriz gerada com sucesso.'))

        print('\n')
        print('Calculando os TF-IDFs dos termos em cada documento e gerando uma matriz...')
        procL.CarregarMatrizTFIDF()
        self.stdout.write(self.style.SUCCESS('Matriz gerada com sucesso.'))

        print('\n')
        print('Calculando as médias dos termos em cada documento e gerando uma matriz...')
        procL.CarregarVetorMedias()
        self.stdout.write(self.style.SUCCESS('Matriz gerada com sucesso.'))

        print('\n')
        print('Calculando os pesos dos termos em cada documento e gerando uma matriz...')
        procL.CarregarMatrizPesos()
        self.stdout.write(self.style.SUCCESS('Matriz gerada com sucesso.'))

        print('\n')
        print('Carregando os pesos para o BD...')
        procL.CarregarPesosBD()
        self.stdout.write(self.style.SUCCESS('Pesos carregados com sucesso.'))

        print('\n')
        print('Gerando os ids dos livros (M x M)...')
        procL.CarregarIdsLivrosMatrizesMM()
        self.stdout.write(self.style.SUCCESS('Ids gerados com sucesso.'))

        print('\n')
        print('Calculando as similaridades entre os documentos e gerando uma matriz...')
        procL.CarregarMatrizSimilaridades()
        self.stdout.write(self.style.SUCCESS('Matriz gerada com sucesso.'))

        print('\n')
        print('Carregando as similaridades para o BD...')
        procL.CarregarSimilaridadesBD()
        self.stdout.write(self.style.SUCCESS('Similaridades carregadas com sucesso.'))
