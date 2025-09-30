class Livro:
    def __init__(self, titulo, autor, ano, isbn, quantidade_exemplares):
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
        self.isbn = isbn
        self.quantidade_total = quantidade_exemplares
        self.quantidade_disponivel = quantidade_exemplares
    
    def emprestar(self):
        if self.quantidade_disponivel > 0:
            self.quantidade_disponivel -= 1
            return True
        else:
            return False
    
    def devolver(self):
        if self.quantidade_disponivel < self.quantidade_total:
            self.quantidade_disponivel += 1

    def __str__(self):
        return f"{self.titulo} - {self.autor} ({self.ano})"

    
