
from pathlib import Path
import sys
import time
import tracemalloc

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from fase2.systemaf2 import ArvoreBinariaBusca, No as NoABB
from fase3.systemaf3 import AVL, No as NoAVL


# Caminho onde estão armazenadas as cargas
PASTA_CARGAS = RAIZ / "cargas"


# Arquivos utilizados nos experimentos
ARQUIVOS_CARGA = [
    ("quase_ordem", 1000, "carga_quase_ordem_1000.txt"),
    ("quase_ordem", 5000, "carga_quase_ordem_5000.txt"),
    ("quase_ordem", 20000, "carga_quase_ordem_20000.txt"),

    ("embaralhada", 1000, "carga_embaralhada_1000.txt"),
    ("embaralhada", 5000, "carga_embaralhada_5000.txt"),
    ("embaralhada", 20000, "carga_embaralhada_20000.txt"),
]


def carregar_registros(caminho):
    """
    Lê um arquivo de carga e retorna somente os registros REG.

    Cada registro é representado por uma tupla:
    (data, horario, linha).
    """

    registros = []

    with open(caminho, "r", encoding="utf-8") as arquivo:
        for numero_linha, linha in enumerate(arquivo, start=1):

            linha = linha.strip()

            # Ignora linhas vazias e comentários
            if not linha or linha.startswith("#"):
                continue

            partes = linha.split()

            # Considera somente operações de registro
            if partes[0] == "REG":

                if len(partes) != 4:
                    raise ValueError(
                        f"Registro inválido na linha {numero_linha}: {linha}"
                    )

                data = partes[1]
                horario = partes[2]
                linha_onibus = partes[3]

                registros.append(
                    (data, horario, linha_onibus)
                )

    return registros


def construir_abb(registros):
    """Constrói uma ABB utilizando os registros recebidos."""

    arvore = ArvoreBinariaBusca()
    inseridos = 0
    duplicados = 0

    for data, horario, linha in registros:
        no = NoABB(data, horario, linha)

        if arvore.inserir(no):
            inseridos += 1
        else:
            duplicados += 1

    return arvore, inseridos, duplicados

def construir_avl(registros):
    """Constrói uma AVL utilizando os registros recebidos."""

    arvore = AVL()
    inseridos = 0
    duplicados = 0

    for data, horario, linha in registros:
        no = NoAVL(data, horario, linha)

        if arvore.inserir(no):
            inseridos += 1
        else:
            duplicados += 1

    return arvore, inseridos, duplicados


def testar_construcao():
    """Compara a quantidade de inserções nas duas árvores."""

    print("\n=== TESTE DE CONSTRUÇÃO DAS ÁRVORES ===\n")

    # Começamos somente com as duas cargas de 1.000 registros.
    arquivos_teste = [
        ARQUIVOS_CARGA[0],
        ARQUIVOS_CARGA[3]
    ]

    for tipo, quantidade, nome_arquivo in arquivos_teste:

        caminho = PASTA_CARGAS / nome_arquivo
        registros = carregar_registros(caminho)

        abb, abb_inseridos, abb_duplicados = construir_abb(registros)
        avl, avl_inseridos, avl_duplicados = construir_avl(registros)

        print(f"Carga: {tipo} ({quantidade} registros)")
        print(f"ABB: {abb_inseridos} inseridos, {abb_duplicados} duplicados")
        print(f"AVL: {avl_inseridos} inseridos, {avl_duplicados} duplicados")

        if abb_inseridos != avl_inseridos:
            raise AssertionError("As árvores inseriram quantidades diferentes!")

        if abb_duplicados != avl_duplicados:
            raise AssertionError("As árvores identificaram duplicatas diferentes!")

        if abb_inseridos + abb_duplicados != len(registros):
            raise AssertionError("Quantidade de registros inconsistente!")

        print("Resultado: OK\n")

        del abb, avl


def testar_leitura_cargas():
    """Confere se os seis arquivos foram carregados corretamente."""

    print("=== TESTE DE LEITURA DAS CARGAS ===\n")

    for tipo, quantidade, nome_arquivo in ARQUIVOS_CARGA:

        caminho = PASTA_CARGAS / nome_arquivo

        if not caminho.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {caminho}"
            )

        registros = carregar_registros(caminho)

        print(f"Carga: {tipo}")
        print(f"Quantidade esperada: {quantidade}")
        print(f"Quantidade encontrada: {len(registros)}")

        if len(registros) != quantidade:
            raise ValueError(
                f"Quantidade incorreta no arquivo {nome_arquivo}"
            )

        print("Primeiros três registros:")

        for registro in registros[:3]:
            print(registro)

        print("-" * 45)


def medir_tempo_construcao(funcao_construcao, registros, repeticoes=5):
    """Mede o tempo de construção de uma árvore em milissegundos."""

    tempos = []

    for _ in range(repeticoes):
        inicio = time.perf_counter()

        arvore, inseridos, duplicados = funcao_construcao(registros)

        fim = time.perf_counter()

        tempos.append((fim - inicio) * 1000)

        del arvore

    tempos.sort()

    mediana = tempos[len(tempos) // 2]

    return mediana, tempos


def testar_tempo():
    """Compara o tempo de construção da ABB e da AVL."""

    print("\n=== TESTE DE TEMPO DE CONSTRUÇÃO ===\n")

    arquivos_teste = [
        ARQUIVOS_CARGA[0],
        ARQUIVOS_CARGA[3]
    ]

    for tipo, quantidade, nome_arquivo in arquivos_teste:

        caminho = PASTA_CARGAS / nome_arquivo
        registros = carregar_registros(caminho)

        tempo_abb, execucoes_abb = medir_tempo_construcao(
            construir_abb, registros
        )

        tempo_avl, execucoes_avl = medir_tempo_construcao(
            construir_avl, registros
        )

        print(f"Carga: {tipo} ({quantidade} registros)")
        print(f"ABB - tempos: {[round(t, 3) for t in execucoes_abb]} ms")
        print(f"ABB - mediana: {tempo_abb:.3f} ms")

        print(f"AVL - tempos: {[round(t, 3) for t in execucoes_avl]} ms")
        print(f"AVL - mediana: {tempo_avl:.3f} ms")

        print("-" * 50)



def medir_altura(raiz):
    """
    Calcula a altura da árvore sem recursão.

    Árvore vazia: altura 0.
    Árvore com apenas a raiz: altura 1.
    """

    if raiz is None:
        return 0

    maior_altura = 0
    pilha = [(raiz, 1)]

    while pilha:
        no, nivel = pilha.pop()

        if nivel > maior_altura:
            maior_altura = nivel

        if no.esquerda is not None:
            pilha.append((no.esquerda, nivel + 1))

        if no.direita is not None:
            pilha.append((no.direita, nivel + 1))

    return maior_altura



def testar_altura():
    """Compara as alturas finais da ABB e da AVL."""

    print("\n=== TESTE DE ALTURA DAS ÁRVORES ===\n")

    arquivos_teste = [
        ARQUIVOS_CARGA[0],
        ARQUIVOS_CARGA[3]
    ]

    for tipo, quantidade, nome_arquivo in arquivos_teste:

        caminho = PASTA_CARGAS / nome_arquivo
        registros = carregar_registros(caminho)

        abb, _, _ = construir_abb(registros)
        avl, _, _ = construir_avl(registros)

        altura_abb = medir_altura(abb.raiz)
        altura_avl = medir_altura(avl.raiz)

        # Confere se a altura armazenada pela AVL está correta.
        if altura_avl != avl.altura():
            raise AssertionError(
                "A altura armazenada pela AVL não corresponde "
                "à altura calculada."
            )

        print(f"Carga: {tipo} ({quantidade} registros)")
        print(f"Altura ABB: {altura_abb}")
        print(f"Altura AVL: {altura_avl}")
        print("-" * 50)

        del abb, avl


def medir_memoria(funcao_construcao, registros):
    """Mede o pico de memória durante a construção da árvore."""

    tracemalloc.start()

    arvore, inseridos, duplicados = funcao_construcao(registros)

    memoria_atual, memoria_pico = tracemalloc.get_traced_memory()

    tracemalloc.stop()

    # Converte bytes para megabytes
    memoria_mb = memoria_pico / (1024 * 1024)

    return arvore, memoria_mb



def testar_memoria():
    """Compara o pico de memória da ABB e da AVL."""

    print("\n=== TESTE DE MEMÓRIA DAS ÁRVORES ===\n")

    arquivos_teste = [
        ARQUIVOS_CARGA[0],
        ARQUIVOS_CARGA[3]
    ]

    for tipo, quantidade, nome_arquivo in arquivos_teste:

        caminho = PASTA_CARGAS / nome_arquivo
        registros = carregar_registros(caminho)

        abb, memoria_abb = medir_memoria(construir_abb, registros)
        del abb

        avl, memoria_avl = medir_memoria(construir_avl, registros)
        del avl

        print(f"Carga: {tipo} ({quantidade} registros)")
        print(f"Memória ABB: {memoria_abb:.4f} MB")
        print(f"Memória AVL: {memoria_avl:.4f} MB")
        print("-" * 50)



if __name__ == "__main__":
    testar_leitura_cargas()
    testar_construcao()
    testar_tempo()
    testar_altura()
    testar_memoria()
