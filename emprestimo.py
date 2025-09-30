from datetime import datetime, timedelta

class Emprestimo:
    def __init__(self, livro, data_emprestimos=None, dias_prazo=7):
        self.livro = livro
        self.data_emprestimos = data_emprestimos or datetime.now()
        self.data_devolucao_prevista = self.data_emprestimos + timedelta(days=dias_prazo)
        self.devolvido = False

    def marcar_devolvido(self):
        self.devolvido = True
        self.livro.devolver()

    def __str__(self):
        status = "Devolvido" if self.devolvido else "Em aberto"
        return f"{self.livro.titulo} até {self.data_devolucao_prevista.strftime('%d/%m/%Y')} ({status})"
    
    
