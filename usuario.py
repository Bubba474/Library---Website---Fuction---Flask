from abc import ABC, abstractmethod

class Usuario(ABC):
    def __init__(self, nome, cpf, email):
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.emprestimos = []  # lista de objetos Emprestimo

    @abstractmethod
    def limite_emprestimos(self):
        pass

    def pode_emprestar(self):
        return len(self.emprestimos) < self.limite_emprestimos()

    def adicionar_emprestimo(self, emprestimo):
        if self.pode_emprestar():
            self.emprestimos.append(emprestimo)
            return True
        return False

    def remover_emprestimo(self, emprestimo):
        if emprestimo in self.emprestimos:
            emprestimo.marcar_devolvido()
            self.emprestimos.remove(emprestimo)

    def qtd_emprestimos_ativos(self):
        # Retorna quantidade de empréstimos que não foram devolvidos
        return sum(1 for e in self.emprestimos if not e.devolvido)

    def __str__(self):
        return f"{self.nome} ({self.__class__.__name__}) - CPF: {self.cpf}"


class Aluno(Usuario):
    def limite_emprestimos(self):
        return 3


class Professor(Usuario):
    def limite_emprestimos(self):
        return 5
