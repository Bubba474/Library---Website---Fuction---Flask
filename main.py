from biblioteca import Biblioteca
from livro import Livro
from usuario import Aluno, Professor
from emprestimo import Emprestimo

# Instância da biblioteca
bib = Biblioteca()

# Cadastro de livros
livros_adicionais = [
    Livro("Algoritmos em Python", "Ana Silva", 2018, "100000001", 3),
    Livro("Redes de Computadores", "Carlos Pereira", 2017, "100000002", 5),
    Livro("Banco de Dados", "Fernanda Lima", 2019, "100000003", 4),
    Livro("Desenvolvimento Web", "Ricardo Alves", 2020, "100000004", 6),
    Livro("Inteligência Artificial", "Marcos Souza", 2021, "100000005", 2),
    Livro("Sistemas Operacionais", "Julia Costa", 2016, "100000006", 3),
    Livro("Engenharia de Software", "Paulo Santos", 2015, "100000007", 5),
    Livro("Computação Gráfica", "Patrícia Gomes", 2019, "100000008", 2),
    Livro("Análise de Algoritmos", "Mariana Rocha", 2018, "100000009", 4),
    Livro("Segurança da Informação", "Eduardo Martins", 2020, "100000010", 3),
    Livro("Programação Funcional", "Aline Ferreira", 2021, "100000011", 2),
    Livro("Matemática Discreta", "Roberto Dias", 2017, "100000012", 5),
    Livro("Teoria da Computação", "Cláudia Nunes", 2019, "100000013", 4),
    Livro("Sistemas Distribuídos", "Sérgio Lima", 2018, "100000014", 3),
    Livro("Redes Neurais", "Tatiana Souza", 2020, "100000015", 2),
    Livro("Big Data", "Gustavo Rocha", 2021, "100000016", 4),
    Livro("Cloud Computing", "Letícia Alves", 2019, "100000017", 3),
    Livro("Programação Concorrente", "Marcelo Pinto", 2017, "100000018", 5),
    Livro("Robótica", "Bruna Oliveira", 2018, "100000019", 2),
    Livro("Criptografia", "Lucas Fernandes", 2020, "100000020", 3),
]

# Cadastrar os livros na biblioteca
for livro in livros_adicionais:
    bib.cadastrar_livro(livro)

# Cadastro de usuários
aluno1 = Aluno("Maria", "111.111.111-11", "maria@email.com")
prof1 = Professor("João", "222.222.222-22", "joao@email.com")

bib.cadastrar_usuario(aluno1)
bib.cadastrar_usuario(prof1)

# Teste de empréstimo: pegar o primeiro livro para emprestar
livro_teste = livros_adicionais[0]  # "Algoritmos em Python"

emprestimo1 = Emprestimo(livro_teste)

if aluno1.adicionar_emprestimo(emprestimo1) and livro_teste.emprestar():
    print(f"Livro emprestado para {aluno1.nome}: {livro_teste.titulo}")
else:
    print("Não foi possível realizar o empréstimo.")

# Teste de devolução
bib.realizar_devolucao("111.111.111-11", "Algoritmos em Python")

print(f"Disponíveis após devolução: {livro_teste.quantidade_disponivel}")
