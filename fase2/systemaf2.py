
from datetime import datetime, timedelta
import sys
import time


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
    if a.data > b.data:
        return 1
    if a.horario < b.horario:
        return -1
    if a.horario > b.horario:
        return 1
    if a.linha < b.linha:
        return -1
    if a.linha > b.linha:
        return 1
    return 0


class ArvoreBinariaBusca:
    def __init__(self):
        self.raiz = None

    def inserir(self, novo_no):
        if self.raiz is None:
            self.raiz = novo_no
            return True

        atual = self.raiz

        while True:
            resultado = comparar(novo_no, atual)

            if resultado == 0:
                return False

            if resultado < 0:
                if atual.esquerda is None:
                    atual.esquerda = novo_no
                    return True
                atual = atual.esquerda
            else:
                if atual.direita is None:
                    atual.direita = novo_no
                    return True
                atual = atual.direita

    def buscar(self, procurado):
        atual = self.raiz

        while atual is not None:
            resultado = comparar(procurado, atual)

            if resultado == 0:
                return True
            if resultado < 0:
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
        return 1 + max(esquerda, direita)

    def proximo(self, data, horario):
        atual = self.raiz
        candidato = None

        while atual is not None:
            if (atual.data, atual.horario) >= (data, horario):
                candidato = atual
                atual = atual.esquerda
            else:
                atual = atual.direita

        return candidato

    def proximo_linha(self, data, horario, linha):
        atual = self.raiz
        candidato = None

        # Percurso em ordem para manter a ordem cronológica.
        pilha = []
        while atual is not None or pilha:
            while atual is not None:
                pilha.append(atual)
                atual = atual.esquerda

            atual = pilha.pop()

            if (
                atual.linha == linha
                and (atual.data, atual.horario) >= (data, horario)
            ):
                candidato = atual
                break

            atual = atual.direita

        return candidato

    def proximo_linha_no_dia(self, data, horario, linha):
        atual = self.raiz
        candidato = None
        pilha = []

        while atual is not None or pilha:
            while atual is not None:
                pilha.append(atual)
                atual = atual.esquerda

            atual = pilha.pop()

            if (
                atual.data == data
                and atual.linha == linha
                and atual.horario >= horario
            ):
                candidato = atual
                break

            atual = atual.direita

        return candidato

    def entre(self, data1, horario1, data2, horario2):
        inicio = (data1, horario1)
        fim = (data2, horario2)
        resultado = []

        if inicio > fim:
            return resultado

        self._entre(self.raiz, inicio, fim, resultado)
        return resultado

    def _entre(self, atual, inicio, fim, resultado):
        if atual is None:
            return

        instante = (atual.data, atual.horario)

        if instante >= inicio:
            self._entre(atual.esquerda, inicio, fim, resultado)

        if inicio <= instante <= fim:
            resultado.append(atual)

        if instante <= fim:
            self._entre(atual.direita, inicio, fim, resultado)

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

        atual.direita, _ = self._remover(atual.direita, sucessor)
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
                inicio = datetime.strptime(horario, "%H:%M:%S")
                fim = datetime.strptime(chegada.horario, "%H:%M:%S")
                espera = int((fim - inicio).total_seconds())
                resultados.append((data_consultada, str(espera)))

        return resultados


def executar_operacao(arvore, partes):
    comando = partes[0]

    if comando == "REG":
        no = No(partes[1], partes[2], partes[3])
        return ["OK" if arvore.inserir(no) else "DUPLICADO"]

    if comando == "BUSCA":
        no = No(partes[1], partes[2], partes[3])
        return ["ACHOU" if arvore.buscar(no) else "NAO"]

    if comando == "PROX":
        no = arvore.proximo(partes[1], partes[2])
        if no is None:
            return ["NENHUM"]
        return [no.data + " " + no.horario + " " + no.linha]

    if comando == "PROXL":
        no = arvore.proximo_linha(partes[1], partes[2], partes[3])
        if no is None:
            return ["NENHUM"]
        return [no.data + " " + no.horario]

    if comando == "ENTRE":
        chegadas = arvore.entre(
            partes[1], partes[2], partes[3], partes[4]
        )
        saida = [str(len(chegadas))]
        for no in chegadas:
            saida.append(no.data + " " + no.horario + " " + no.linha)
        return saida

    if comando == "REM":
        no = No(partes[1], partes[2], partes[3])
        return ["OK" if arvore.remover(no) else "NAO"]

    if comando == "ALT":
        return [str(arvore.altura())]

    if comando == "SEMANA":
        resultados = arvore.espera_semanal(
            partes[1], partes[2], partes[3], int(partes[4])
        )
        return [data + " " + espera for data, espera in resultados]

    return []


def main():
    if len(sys.argv) != 2:
        print(
            "Uso: python sistema.py arquivo.txt",
            file=sys.stderr
        )
        return

    with open(sys.argv[1], "r", encoding="utf-8") as arquivo:
        operacoes = []

        for linha in arquivo:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                operacoes.append(linha.split())

    arvore = ArvoreBinariaBusca()
    saidas = []

    inicio = time.perf_counter()

    for partes in operacoes:
        saidas.extend(executar_operacao(arvore, partes))

    duracao_ms = (time.perf_counter() - inicio) * 1000

    for linha in saidas:
        print(linha)

    print(f"TEMPO_MS {duracao_ms:.3f}", file=sys.stderr)


if __name__ == "__main__":
    main()
