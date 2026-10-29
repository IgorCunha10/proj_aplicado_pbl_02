class Chegada:
    def __init__(self, data, horario, linha):
        self.data = data
        self.horario = horario
        self.linha = linha

class No:
    def __init__(self, data, horario, linha):
        self.data = data
        self.horario = horario
        self.linha = linha

        self.esquerda = None
        self.direita = None


no = No("2026-10-28","18:30:00", "136.1")
print(no.data)
print(no.horario)
print(no.linha)
print(no.esquerda)
print(no.direita)


