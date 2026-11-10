#!/usr/bin/env python3

# mesma coisa da Fase 2, mas a árvore é avl

# O que muda da fase 2:
# No.altura  -> guarda altura do nó
# h() / atualizar() / fator() -> balanceamento da arvore
# rot_esq() / rot_dir() -> simples
# rot dupla = 2 simples
# inserir_avl() e remover_avl() recursivos com rebalanceamento
# Índice auxiliar para R4/R8 (sem usar dict pronto) -> tem hash simples + lista ordenada por linha

# Uso: mesma coisa do uso de antes, eu acho.
# python systemaf3.py arquivo.txt  (stdout=respostas, stderr=TEMPO_MS)

import sys
import time
from datetime import datetime, timedelta
# sys.setrecursionlimit(1000000) # antes ele quebrava passando o limite

# nó AVL
class No:
    __slots__ = ("data","horario","linha","esquerda","direita","altura")
    def __init__(self, data, horario, linha):
        self.data = data
        self.horario = horario
        self.linha = linha
        self.esquerda = None
        self.direita = None
        self.altura = 1  # adicionado

def comparar(a,b):
    if a.data < b.data: return -1
    if a.data > b.data: return 1
    if a.horario < b.horario: return -1
    if a.horario > b.horario: return 1
    if a.linha < b.linha: return -1
    if a.linha > b.linha: return 1
    return 0

#  helpers do AVL 
def h(no): return no.altura if no else 0
def atualizar(no): no.altura = 1 + max(h(no.esquerda), h(no.direita))
def fator(no): return h(no.esquerda) - h(no.direita) if no else 0

def rot_dir(y):
    """rotação direita - caso esquerda-esquerda"""
    x = y.esquerda
    T2 = x.direita
    x.direita = y
    y.esquerda = T2
    atualizar(y); atualizar(x)
    return x

def rot_esq(x):
    """rotação esquerda - caso direita-direita (espelho)"""
    y = x.direita
    T2 = y.esquerda
    y.esquerda = x
    x.direita = T2
    atualizar(x); atualizar(y)
    return y

def balancear(no):
    """chamar após atualizar(no)."""
    f = fator(no)
    # esquerda pesada
    if f > 1:
        if fator(no.esquerda) < 0: # esquerda-direita -> dupla
            no.esquerda = rot_esq(no.esquerda)
        return rot_dir(no)
    # direita pesada
    if f < -1:
        if fator(no.direita) > 0: # direita-esquerda -> dupla
            no.direita = rot_dir(no.direita)
        return rot_esq(no)
    return no

# indice auxiliar para R4/R8 sem dict
# hash simples com chaining, só usa list/tupla. cada linha guarda lista por (data,horario).
class HashIndiceLinha:
    def __init__(self, m=2048):
        self.m = m
        self.buckets = [[] for _ in range(m)]

    def _hash(self, linha):
        hv = 0
        for c in linha:
            hv = (hv*131 + ord(c)) % self.m
        return hv

    def _get_bucket_entry(self, linha):
        b = self.buckets[self._hash(linha)]
        for i,(k, lst) in enumerate(b):
            if k == linha:
                return b, i, lst
        return b, -1, None

    def obter_lista(self, linha):
        b, idx, lst = self._get_bucket_entry(linha)
        if lst is not None:
            return lst
        # cria nova
        nova = []
        b.append((linha, nova))
        return nova

    def inserir_ordenado(self, no):
        lst = self.obter_lista(no.linha)
        # inserção ordenada por (data,horario) via busca binária manual (sem bisect)
        lo, hi = 0, len(lst)
        chave = (no.data, no.horario)
        while lo < hi:
            mid = (lo+hi)//2
            if (lst[mid].data, lst[mid].horario) < chave:
                lo = mid+1
            else:
                hi = mid
        lst.insert(lo, no)

    def remover(self, data, horario, linha):
        b, idx, lst = self._get_bucket_entry(linha)
        if lst is None: return False
        lo, hi = 0, len(lst)
        chave = (data, horario)
        while lo < hi:
            mid = (lo+hi)//2
            if (lst[mid].data, lst[mid].horario) < chave:
                lo = mid+1
            else:
                hi = mid
        if lo < len(lst) and lst[lo].data == data and lst[lo].horario == horario:
            lst.pop(lo)
            # se lista ficou vazia, pode remover entrada do bucket (ou nao, pois é opcional)
            return True
        return False

    def proximo_linha(self, data, horario, linha):
        b, idx, lst = self._get_bucket_entry(linha)
        if lst is None or not lst: return None
        lo, hi = 0, len(lst)
        chave = (data, horario)
        while lo < hi:
            mid = (lo+hi)//2
            if (lst[mid].data, lst[mid].horario) < chave:
                lo = mid+1
            else:
                hi = mid
        return lst[lo] if lo < len(lst) else None

    def proximo_no_dia(self, data, horario, linha):
        no = self.proximo_linha(data, horario, linha)
        if no and no.data == data:
            return no
        return None

# AVL principal
class AVL:
    def __init__(self):
        self.raiz = None
        self.indice = HashIndiceLinha() # para R4/R8

    # R1 
    def inserir(self, novo):
        # verifica duplicado antes
        if self._buscar_no(self.raiz, novo):
            return False
        self.raiz = self._inserir(self.raiz, novo)
        self.indice.inserir_ordenado(novo)
        return True

    def _inserir(self, no, novo):
        if no is None: return novo
        r = comparar(novo, no)
        if r < 0: no.esquerda = self._inserir(no.esquerda, novo)
        elif r > 0: no.direita = self._inserir(no.direita, novo)
        else: return no
        atualizar(no)
        return balancear(no)

    def _buscar_no(self, no, alvo):
        while no:
            r = comparar(alvo, no)
            if r==0: return True
            no = no.esquerda if r<0 else no.direita
        return False

    # R2 
    def buscar(self, alvo):
        return self._buscar_no(self.raiz, alvo)

    # R6 (decisão 3.1 do relatório: remoção com sucessor + rebalanceamento)
    def remover(self, alvo):
        if not self._buscar_no(self.raiz, alvo):
            return False
        self.raiz = self._remover(self.raiz, alvo)
        self.indice.remover(alvo.data, alvo.horario, alvo.linha)
        return True

    def _remover(self, no, alvo):
        if no is None: return None
        r = comparar(alvo, no)
        if r < 0:
            no.esquerda = self._remover(no.esquerda, alvo)
        elif r > 0:
            no.direita = self._remover(no.direita, alvo)
        else: # achou
            if no.esquerda is None: return no.direita
            if no.direita is None: return no.esquerda
            # 2 filhos: sucessor (menor da direita)
            suc = no.direita
            while suc.esquerda: suc = suc.esquerda
            no.data, no.horario, no.linha = suc.data, suc.horario, suc.linha
            # remove sucessor lá embaixo (não mexe no índice aqui, já foi removido acima)
            # remover sucessor sem tocar no índice de novo -> chama remoção interna sem índice
            no.direita = self._remover_sem_indice(no.direita, suc)
        if no:
            atualizar(no)
            no = balancear(no)
        return no

    def _remover_sem_indice(self, no, alvo):
        # igual ao _remover so que nao toquei no índice auxiliar
        if no is None: return None
        r = comparar(alvo, no)
        if r < 0: no.esquerda = self._remover_sem_indice(no.esquerda, alvo)
        elif r > 0: no.direita = self._remover_sem_indice(no.direita, alvo)
        else:
            if no.esquerda is None: return no.direita
            if no.direita is None: return no.esquerda
            suc = no.direita
            while suc.esquerda: suc = suc.esquerda
            no.data, no.horario, no.linha = suc.data, suc.horario, suc.linha
            no.direita = self._remover_sem_indice(no.direita, suc)
        if no:
            atualizar(no)
            return balancear(no)
        return no

    # R7 
    def altura(self):
        return h(self.raiz) # altura já tá calculada O(1)

    # R3 
    def proximo(self, data, horario):
        probe = No(data, horario, "")
        atual, cand = self.raiz, None
        while atual:
            if comparar(probe, atual) <= 0:
                cand = atual; atual = atual.esquerda
            else:
                atual = atual.direita
        return cand

    # R4  (usa índice -> O(log n) em vez de O(n) pra varrer a árvore)
    def proximo_linha(self, data, horario, linha):
        return self.indice.proximo_linha(data, horario, linha)

    # R5 
    def entre(self, d1,h1,d2,h2):
        ini=(d1,h1); fim=(d2,h2)
        if ini>fim: return []
        res=[]
        self._entre(self.raiz, ini, fim, res)
        return res
    def _entre(self, no, ini, fim, res):
        if no is None: return
        inst=(no.data, no.horario)
        if inst >= ini: self._entre(no.esquerda, ini, fim, res)
        if ini <= inst <= fim: res.append(no)
        if inst <= fim: self._entre(no.direita, ini, fim, res)

    # R8 
    def espera_semanal(self, linha, data, horario, k):
        data_final = datetime.strptime(data, "%Y-%m-%d").date()
        data_ini = data_final - timedelta(weeks=k-1)
        consulta_seg = int(horario[0:2])*3600 + int(horario[3:5])*60 + int(horario[6:8])
        out=[]
        for i in range(k):
            dia = data_ini + timedelta(weeks=i)
            dstr = dia.strftime("%Y-%m-%d")
            chegada = self.indice.proximo_no_dia(dstr, horario, linha)
            if chegada is None:
                out.append((dstr,"NAOPASSOU"))
            else:
                espera = (int(chegada.horario[0:2])*3600 + int(chegada.horario[3:5])*60 + int(chegada.horario[6:8])) - consulta_seg
                out.append((dstr,str(espera)))
        return out

# I/O igual Fase 2 
def executar(arv, partes):
    cmd=partes[0]
    if cmd=="REG":
        return ["OK" if arv.inserir(No(partes[1],partes[2],partes[3])) else "DUPLICADO"]
    if cmd=="BUSCA":
        return ["ACHOU" if arv.buscar(No(partes[1],partes[2],partes[3])) else "NAO"]
    if cmd=="PROX":
        n=arv.proximo(partes[1],partes[2]); return ["NENHUM" if not n else f"{n.data} {n.horario} {n.linha}"]
    if cmd=="PROXL":
        n=arv.proximo_linha(partes[1],partes[2],partes[3]); return ["NENHUM" if not n else f"{n.data} {n.horario}"]
    if cmd=="ENTRE":
        lst=arv.entre(partes[1],partes[2],partes[3],partes[4]); out=[str(len(lst))]
        for n in lst: out.append(f"{n.data} {n.horario} {n.linha}")
        return out
    if cmd=="REM":
        return ["OK" if arv.remover(No(partes[1],partes[2],partes[3])) else "NAO"]
    if cmd=="ALT":
        return [str(arv.altura())]
    if cmd=="SEMANA":
        return [f"{d} {e}" for d,e in arv.espera_semanal(partes[1],partes[2],partes[3],int(partes[4]))]
    return []

def main():
    if len(sys.argv)!=2:
        print("Uso: python sistema_avl.py arquivo.txt", file=sys.stderr); return
    ops=[]
    with open(sys.argv[1],encoding="utf-8") as f:
        for l in f:
            l=l.strip()
            if l and not l.startswith("#"): ops.append(l.split())
    avl=AVL()
    t0=time.perf_counter()
    saidas=[]
    for p in ops: saidas.extend(executar(avl,p))
    dt=(time.perf_counter()-t0)*1000
    for s in saidas: print(s)
    print(f"TEMPO_MS {dt:.3f}", file=sys.stderr)

if __name__=="__main__": main()
