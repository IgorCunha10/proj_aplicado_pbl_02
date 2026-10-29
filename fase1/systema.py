import os
from datetime import datetime, timedelta
# nao tava reconhecendo, mesmo estando na mesma pasta, entao coloquei esse os que resolve o problema
pasta_do_script = os.path.dirname(os.path.abspath(__file__))
c1k_embaralhado = os.path.join(pasta_do_script, "carga_embaralhada_1000.txt") 
c1k_ordenado = os.path.join(pasta_do_script, "carga_quase_ordem_1000.txt") 
# 5k
c5k_embaralhado = os.path.join(pasta_do_script, "carga_embaralhada_1000.txt") 
c5k_ordenado = os.path.join(pasta_do_script, "carga_quase_ordem_5000.txt") 
# 20k
c20k_embaralhado = os.path.join(pasta_do_script, "carga_embaralhada_20000.txt") 
c20k_ordenado = os.path.join(pasta_do_script, "carga_quase_ordem_20000.txt") 

# steiner: eu preciso colocar a carga na arvore binaria, vou tentar colocar o separador da fase 1 vetorial q era errado
chegadas = [] # vetor temporario tb

# ATENCAO ::: PARA MUDAR A CARGA, MUDE O C1K_EMBARALHADO PARA C5K_ORDENADO, C20K_EMBARALHADO, VCS ENTENDERAM
with open(c1k_embaralhado, "r", encoding="utf-8") as arquivo:
    for linha in arquivo:
        partes = linha.strip().split()
        if not partes:
            continue # ele pula as linhas

        comando = partes[0] # registra o REG
        if comando == "REG" and len(partes) >= 4:
            chegadas.append((partes[1], partes[2], partes[3]))

    
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

    def buscar_chegada(self, procurado):
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

    def remover_chegada(self, procurado):
        self.raiz, removido = self._remover_chegada(self.raiz, procurado)
        return removido

    def _remover_chegada(self, atual, procurado):
        if atual is None:
            return None, False

        resultado = comparar(procurado, atual)

        if resultado < 0:
            atual.esquerda, removido = self._remover_chegada(
                atual.esquerda, procurado
            )
            return atual, removido

        if resultado > 0:
            atual.direita, removido = self._remover_chegada(
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

        atual.direita, _ = self._remover_chegada(
            atual.direita, sucessor
        )

        return atual, True

def semana(linha, data, horario, k):
    base = datetime.fromisoformat(f"{data} {horario}")

    for i in range(k - 1, -1, -1):
        consulta = base - timedelta(weeks=i)
        dia = str(consulta.date())
        bus = arvore.proximo_linha(dia, horario, linha)

        if bus and bus.data == dia:
            chegada = datetime.fromisoformat(f"{bus.data} {bus.horario}")
            espera = int((chegada - consulta).total_seconds())
            print(dia, espera)
        else:
            print(dia, "data NAO PASSOU")

arvore = ArvoreBinariaBusca()

for registro in chegadas:
    arvore.inserir(No(*registro))

teste_chegada = No("2026-10-29", "21:03:17", "0.136") # R1 registrar (colocar valor aqui) OK = já tem // DUPLICADO = valor inedito
resultado = arvore.inserir(teste_chegada)

if resultado: # R1 registrar
    print("OK")
else:
    print("DUPLICADO")

procurado = No("2026-10-26", "09:58:41", "136.5") # R2 busca (colocar valor aqui)
resultado = arvore.buscar_chegada(procurado) # R2 busca

if resultado: # R2 busca
    print("ACHOU")
else:
    print("NAO")

print(arvore.altura()) # R7 altura

resultado = arvore.proximo("2026-10-28", "18:15:00") # R3 proximo (colocar valor aqui)

if resultado is None: #R3 proximo
    print("NENHUM")
else:
    print(resultado.data, resultado.horario, resultado.linha)

resultado = arvore.proximo_linha("2026-10-28", "18:15:00", "110") # R4 proximo linha (colocar valor aqui)

if resultado is None: # R4 proximo_linha
    print("NENHUM")
else:
    print((resultado.data), (resultado.horario))

data1, horario1 = "2026-10-28", "18:00:00" # R5 entre (colocar valores aqui)
data2, horario2 = "2026-10-28", "19:00:00" # R5 entre (colocar valores aqui)

if (data1, horario1) > (data2, horario2):
    print(0)
else:
    resultado_entre = arvore.entre(data1, horario1, data2, horario2)
    print(len(resultado_entre))
    for no in resultado_entre:
        print(no.data, no.horario, no.linha)

semana("110", "2026-10-28", "18:15:00", 4) # R8 espera semanal

