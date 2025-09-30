class Biblioteca:
    def __init__(self):
        self.livros = []
        self.usuarios = []

    def cadastrar_livro(self, livro):
        self.livros.append(livro)

    def cadastrar_usuario(self, usuario):
        self.usuarios.append(usuario)

    def encontrar_usuario_por_cpf(self, cpf):
        for usuario in self.usuarios:
            if usuario.cpf == cpf:
                return usuario
        return None

    def encontrar_livro_por_titulo(self, titulo):
        for livro in self.livros:
            if livro.titulo.lower() == titulo.lower():
                return livro
        return None

    def realizar_devolucao(self, cpf_usuario, titulo_livro):
        usuario = self.encontrar_usuario_por_cpf(cpf_usuario)
        if not usuario:
            print("Usuário não encontrado")
            return

        for emprestimo in usuario.emprestimos:
            if emprestimo.livro.titulo.lower() == titulo_livro.lower() and not emprestimo.devolvido:
                usuario.remover_emprestimo(emprestimo)
                print(f"Livro '{emprestimo.livro.titulo}' devolvido por {usuario.nome}")
                return

        print("Empréstimo ativo não encontrado para esse livro.")

    def remover_emprestimo(self, emprestimo):
        if emprestimo in self.emprestimos:
            emprestimo.marcar_devolvido()
            self.emprestimos.remove(emprestimo)