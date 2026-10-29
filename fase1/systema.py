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


def comparar(a, b):
    if a.data < b.data:
        return -1
    elif a.data > b.data:
        return 1
    elif a.horario < b.horario:
        return -1
    elif a.horario > b.horario:
        return 1
    elif a.linha < b.linha:
        return -1
    elif a.linha > b.linha:
        return 1
    else:
        return 0


class ArvoreBinariaBusca:
    def __init__(self):
        self.raiz = None

    def inserir(self, novo_no):
        if self.raiz is None:
            self.raiz = novo_no
            return True

        atual = self.raiz
        pai = None

        while atual is not None:
            pai = atual
            resultado = comparar(novo_no, atual)

            if resultado == -1:
                atual = atual.esquerda
            elif resultado == 1:
                atual = atual.direita
            else:
                return False

        if comparar(novo_no, pai) == -1:
            pai.esquerda = novo_no
        else:
            pai.direita = novo_no

        return True

    def buscar(self, procurado):
        atual = self.raiz

        while atual is not None:
            resultado = comparar(procurado, atual)

            if resultado == 0:
                return True
            elif resultado == -1:
                atual = atual.esquerda
            else:
                atual = atual.direita

        return False

    def altura(self):
        return self._altura(self.raiz)

    def _altura(self, atual):
        if atual is None:
            return 0

        esquerda = self._altura(atual.esquerda)
        direita = self._altura(atual.direita)

        if esquerda > direita:
            return esquerda + 1
        else:
            return direita + 1


arvore = ArvoreBinariaBusca()

arvore.inserir(No("2026-10-28", "18:30:00", "136"))
arvore.inserir(No("2026-10-28", "18:00:00", "110"))
arvore.inserir(No("2026-10-28", "19:00:00", "170"))

procurado = No("2026-10-28", "18:00:00", "136.1")
resultado = arvore.buscar(procurado)

if resultado:
    print("ACHOU")
else:
    print("NAO ACHOU")

print(arvore.altura())


