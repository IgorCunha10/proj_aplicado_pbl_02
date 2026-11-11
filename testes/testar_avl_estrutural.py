import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from fase3.systemaf3 import AVL, No


def verificar_arvore(no, minimo=None, maximo=None):
    """Confere ordenação, alturas armazenadas e fator AVL em toda a árvore."""
    if no is None:
        return 0
    chave = (no.data, no.horario, no.linha)
    assert minimo is None or minimo < chave, f"Ordenação inválida: {chave} <= {minimo}"
    assert maximo is None or chave < maximo, f"Ordenação inválida: {chave} >= {maximo}"

    he = verificar_arvore(no.esquerda, minimo, chave)
    hd = verificar_arvore(no.direita, chave, maximo)
    altura_correta = 1 + max(he, hd)
    assert no.altura == altura_correta, (
        f"Altura incorreta em {chave}: armazenada={no.altura}, correta={altura_correta}"
    )
    assert abs(he - hd) <= 1, f"Nó desbalanceado {chave}: FE={he-hd}"
    return altura_correta

def criar_arvore(valores):
    arvore = AVL()

    for data, horario, linha in valores:
        no = No(data, horario, linha)
        arvore.inserir(no)

    return arvore


def testar_balanceamento():
    casos = {
        "LL": [30, 20, 10],
        "RR": [10, 20, 30],
        "LR": [30, 10, 20],
        "RL": [10, 30, 20]
    }

    for nome, valores in casos.items():
        entradas = [
            ("2026-01-01", f"{valor:02d}:00", "L1")
            for valor in valores
        ]

        arvore = criar_arvore(entradas)

        verificar_arvore(arvore.raiz)

        assert arvore.raiz.data == "2026-01-01"
        assert arvore.raiz.horario == "20:00"

        print(f"[OK] Rotação {nome}")


def testar_remocoes():
    valores = [
        ("2026-01-01", "10:00", "L1"),
        ("2026-01-01", "05:00", "L1"),
        ("2026-01-01", "15:00", "L1"),
        ("2026-01-01", "03:00", "L1"),
        ("2026-01-01", "07:00", "L1"),
        ("2026-01-01", "12:00", "L1"),
        ("2026-01-01", "18:00", "L1")
    ]

    arvore = criar_arvore(valores)

    removidos = [
        ("2026-01-01", "03:00", "L1"),
        ("2026-01-01", "15:00", "L1"),
        ("2026-01-01", "10:00", "L1")
    ]

    for data, horario, linha in removidos:
        no = No(data, horario, linha)
        arvore.remover(no)
        verificar_arvore(arvore.raiz)

    print("[OK] Remoções e balanceamento")


if __name__ == "__main__":
    testar_balanceamento()
    testar_remocoes()

    print("\nTodos os testes estruturais passaram!")