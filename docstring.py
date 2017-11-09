'''
------------------------------------------ COMANDOS VÁLIDOS USUÁRIO ------------------------------------------

1. import ProcessamentoUsuarios
    Descrição:
        Este comando importa o pacote usuario.libs.py, desenvolvido no projeto bibinterativa.

    Utilização:
        from <nome_do_app>.libs import <Classe>

    Parâmetros:
        N/A

    Retornos:
        N/A

2. ProcessamentoUsuarios
    Descrição:
        Este método cria uma instância da classe ProcessamentoUsuarios e cadastra ou recupera um usuário da base.

    Utilização:
        objeto = metodo_construtor(<param1>, <param2>, <param3>, <param4>)

    Parâmetros:
        param1
            Nome do usuário ou login (texto)
        param2
            Nome principal (texto)
        param3
            Sobrenome (texto)
        param4
            E-mail (texto)

    Retornos:
        retorno1
            Objeto da classe ProcessamentoUsuarios com um novo usuário cadastrado

3. PesquisarPalavraChave
    Descrição:
        Este método executa pesquisa na base de livros por título dos livros e apresenta o resultado da pesquisa com o ID e o título de cada livro (10 livros por padrão).

    Utilização:
        objeto.PesquisarPalavraChave(<param1>)

    Parâmetros:
        param1
            Texto a ser pesquisado (texto)

    Retornos:
        N/A

4. SelecionarLivros
    Descrição:
        Este método adiciona o(s) ID(s) do(s) livro(s) a uma lista de livros selecionados (já lidos ou da preferência do usuário) e apresenta a lista atualizada com o ID e o título de cada livro. O ID deve ter sido apresentado como resultado na última pesquisa realizada e não deve pertencer previamente na lista dos selecionados.

    Utilização:
        objeto.SelecionarLivros(<param1>)

    Parâmetros:
        param1
            IDs dos livros a serem selecionados do resultado da pesquisa (lista)

    Retornos:
        N/A

5. DesmarcarLivros
    Descrição:
        Este método exclui o(s) ID(s) do(s) livro(s) de uma lista de livros selecionados (já lidos ou da preferência do usuário) e apresenta a lista atualizada com o ID e o título de cada livro. O ID deve pertencer previamente a lista de selecionados.

    Utilização:
        objeto.DesmarcarLivros(<param1>)

    Parâmetros:
        param1
            IDs dos livros a serem excluídos da lista de seleção (lista)

    Retornos:
        N/A

6. LimparSelecao
    Descrição:
        Este método exclui todos os livros da lista de livros selecionados (já lidos ou da preferência do usuário) e apresenta a lista vazia atualizada.

    Utilização:
        objeto.LimparSelecao()

    Parâmetros:
        N/A

    Retornos:
        N/A

7. EnviarLivrosSelecionados
    Descrição:
        Este método conclui a lista de livros selecionados e envia a mesma para ser processada e são calculadas as recomendações para cada livro selecionado (2 livros por padrão para cada livro selecionado) e, por fim, apresenta os livros selecionados e recomendados.

    Utilização:
        objeto.EnviarLivrosSelecionados()

    Parâmetros:
        N/A

    Retornos:
        N/A

8. ExplorarLivro
    Descrição:
        Este método apresenta todas informações sobre um dado livro (ID, título, autor(es), editora, ano de publicação e descrição), conforme o ID passado ao mesmo.

    Utilização:
        objeto.ExplorarLivro(param1)

    Parâmetros:
        param1
            ID a ser explorado

    Retornos:
        N/A

9. EnviarRatings
    Descrição:
        Este método envia todas as avaliações realizadas pelo usuário sobre os livros recomendados e apresenta uma mensagem de sucesso ao final. Todos os livros recomendados devem ser avaliados.

    Utilização:
        objeto.EnviarRatings(param1)

    Parâmetros:
        param1
            Ratings dos livros recomendados (1 para gostei e 0 para não gostei)

    Retornos:
        N/A
'''
