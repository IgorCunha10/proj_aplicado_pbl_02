from datetime import datetime, timedelta

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

    def proximo(self, data, horario):
        procurado = No(data, horario, "")
        atual = self.raiz
        candidato = None

        while atual is not None:
            resultado = comparar(procurado, atual)

            if resultado <= 0:
                candidato = atual
                atual = atual.esquerda
            else:
                atual = atual.direita

        return candidato

    def proximo_linha(self, data, horario, linha):
        candidato = None
        pilha = [self.raiz]

        while pilha:
            atual = pilha.pop()

            if atual is None:
                continue

            instante_atual = (atual.data, atual.horario)
            instante_consulta = (data, horario)

            if atual.linha == linha and instante_atual >= instante_consulta:
                if candidato is None:
                    candidato = atual
                elif instante_atual < (candidato.data, candidato.horario):
                    candidato = atual

            pilha.append(atual.esquerda)
            pilha.append(atual.direita)

        return candidato

    def proximo_linha_no_dia(self, data, horario, linha):
        candidato = None
        pilha = [self.raiz]

        while pilha:
            atual = pilha.pop()

            if atual is None:
                continue

            if atual.data == data and atual.linha == linha:
                if atual.horario >= horario:
                    if candidato is None or atual.horario < candidato.horario:
                        candidato = atual

            pilha.append(atual.esquerda)
            pilha.append(atual.direita)

        return candidato

    def entre(self, data1, horario1, data2, horario2):
        resultado = []
        self._entre(self.raiz, data1, horario1, data2, horario2, resultado)
        return resultado

    def _entre(self, atual, data1, horario1, data2, horario2, resultado):
        if atual is None:
            return

        instante = (atual.data, atual.horario)
        inicio = (data1, horario1)
        fim = (data2, horario2)

        self._entre(atual.esquerda, data1, horario1, data2, horario2, resultado)

        if inicio <= instante <= fim:
            resultado.append(atual)

        self._entre(atual.direita, data1, horario1, data2, horario2, resultado)

    def remover(self, procurado):
        self.raiz, removido = self._remover(self.raiz, procurado)
        return removido

    def _remover(self, atual, procurado):
        if atual is None:
            return None, False

        resultado = comparar(procurado, atual)

        if resultado < 0:
            atual.esquerda, removido = self._remover(
                atual.esquerda, procurado
            )
            return atual, removido

        if resultado > 0:
            atual.direita, removido = self._remover(
                atual.direita, procurado
            )
            return atual, removido


        if atual.esquerda is None:
            return atual.direita, True

        if atual.direita is None:
            return atual.esquerda, True

        sucessor = atual.direita

        while sucessor.esquerda is not None:
            sucessor = sucessor.esquerda

        atual.data = sucessor.data
        atual.horario = sucessor.horario
        atual.linha = sucessor.linha

        atual.direita, _ = self._remover(
            atual.direita, sucessor
        )

        return atual, True

    def espera_semanal(self, linha, data, horario, k):
        resultados = []

        data_final = datetime.strptime(data, "%Y-%m-%d").date()
        data_inicial = data_final - timedelta(weeks=k - 1)

        for i in range(k):
            dia = data_inicial + timedelta(weeks=i)
            data_consultada = dia.strftime("%Y-%m-%d")

            chegada = self.proximo_linha_no_dia(
                data_consultada, horario, linha
            )

            if chegada is None:
                resultados.append((data_consultada, "NAOPASSOU"))
            else:
                hora_inicio = datetime.strptime(
                    horario, "%H:%M:%S"
                )
                hora_chegada = datetime.strptime(
                    chegada.horario, "%H:%M:%S"
                )

                espera = int((hora_chegada - hora_inicio).total_seconds())

                resultados.append((data_consultada, str(espera)))

        return resultados


arvore = ArvoreBinariaBusca()

while True:
    try:
        entrada = input()
    except EOFError:
        break

    entrada = entrada.strip()

    if not entrada or entrada.startswith("#"):
        continue

    partes = entrada.split()
    comando = partes[0]

    if comando == "REG":
        data = partes[1]
        horario = partes[2]
        linha = partes[3]

        novo_no = No(data, horario, linha)

        if arvore.inserir(novo_no):
            print("OK")
        else:
            print("DUPLICADO")

    elif comando == "BUSCA":
        data = partes[1]
        horario = partes[2]
        linha = partes[3]

        procurado = No(data, horario, linha)

        if arvore.buscar(procurado):
            print("ACHOU")
        else:
            print("NAO")

    elif comando == "ALT":
        print(arvore.altura())

    elif comando == "SEMANA":
        linha = partes[1]
        data = partes[2]
        horario = partes[3]
        k = int(partes[4])

        resultados = arvore.espera_semanal(
            linha, data, horario, k
        )

        for data_consultada, espera in resultados:
            print(data_consultada, espera)

    elif comando == "ENTRE":
        data1 = partes[1]
        horario1 = partes[2]
        data2 = partes[3]
        horario2 = partes[4]

        resultados = arvore.entre(data1, horario1, data2, horario2)

        print(len(resultados))

        for chegada in resultados:
            print(chegada.data, chegada.horario, chegada.linha)




