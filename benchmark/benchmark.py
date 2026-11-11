
from pathlib import Path
import sys
import time
import tracemalloc
import statistics
import csv
import math

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

    mediana = statistics.median(tempos)

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



def medir_memoria(funcao_construcao, registros, repeticoes=5):
    """Mede o pico de memória em cinco construções."""

    medicoes = []

    for _ in range(repeticoes):
        tracemalloc.start()

        arvore, inseridos, duplicados = funcao_construcao(registros)

        memoria_atual, memoria_pico = tracemalloc.get_traced_memory()

        tracemalloc.stop()

        memoria_mb = memoria_pico / (1024 * 1024)
        medicoes.append(memoria_mb)

        del arvore

    mediana = statistics.median(medicoes)

    return mediana, medicoes



def testar_memoria():
    """Compara a mediana do pico de memória da ABB e AVL."""

    print("\n=== TESTE DE MEMÓRIA DAS ÁRVORES ===\n")

    arquivos_teste = [
        ARQUIVOS_CARGA[0],
        ARQUIVOS_CARGA[3]
    ]

    for tipo, quantidade, nome_arquivo in arquivos_teste:

        caminho = PASTA_CARGAS / nome_arquivo
        registros = carregar_registros(caminho)

        memoria_abb, execucoes_abb = medir_memoria(
            construir_abb, registros
        )

        memoria_avl, execucoes_avl = medir_memoria(
            construir_avl, registros
        )

        print(f"Carga: {tipo} ({quantidade} registros)")

        print(
            f"ABB - mediana: {memoria_abb:.4f} MB"
        )

        print(
            f"AVL - mediana: {memoria_avl:.4f} MB"
        )

        print("-" * 50)


def executar_benchmark_completo():
    """Executa todos os experimentos ABB x AVL."""

    print("\n=== BENCHMARK COMPLETO ABB x AVL ===\n")

    resultados = []

    for tipo, quantidade, nome_arquivo in ARQUIVOS_CARGA:

        caminho = PASTA_CARGAS / nome_arquivo
        registros = carregar_registros(caminho)

        print(f"\nCarga: {tipo} ({quantidade} registros)")

        # Construção inicial para verificar inserções e duplicatas.
        abb, abb_inseridos, abb_duplicados = construir_abb(registros)
        avl, avl_inseridos, avl_duplicados = construir_avl(registros)

        if abb_inseridos != avl_inseridos:
            raise AssertionError("Quantidade de inserções diferente!")

        if abb_duplicados != avl_duplicados:
            raise AssertionError("Quantidade de duplicatas diferente!")

        # Medição das alturas.
        altura_abb = medir_altura(abb.raiz)
        altura_avl = medir_altura(avl.raiz)

        if altura_avl != avl.altura():
            raise AssertionError("Altura armazenada da AVL incorreta!")

        # Verificação do limite teórico da AVL.
        limite_avl = 1.45 * math.log2(abb_inseridos + 2)

        if altura_avl > limite_avl:
            raise AssertionError("A AVL ultrapassou o limite de altura!")

        # Libera as árvores da construção inicial.
        del abb, avl

        # Medição de tempo: cinco execuções.
        tempo_abb, tempos_abb = medir_tempo_construcao(
            construir_abb, registros
        )

        tempo_avl, tempos_avl = medir_tempo_construcao(
            construir_avl, registros
        )

        # Medição de memória: cinco execuções.
        memoria_abb, memorias_abb = medir_memoria(
            construir_abb, registros
        )

        memoria_avl, memorias_avl = medir_memoria(
            construir_avl, registros
        )

        # Armazena os resultados do cenário.
        resultado = {
            "distribuicao": tipo,
            "quantidade_registros": quantidade,
            "registros_inseridos": abb_inseridos,
            "duplicados": abb_duplicados,
            "primeiros_7_registros": registros[:7],
            "tempo_mediano_abb_ms": tempo_abb,
            "tempo_mediano_avl_ms": tempo_avl,
            "altura_abb": altura_abb,
            "altura_avl": altura_avl,
            "limite_altura_avl": limite_avl,
            "avl_dentro_limite": altura_avl <= limite_avl,
            "memoria_mediana_abb_mb": memoria_abb,
            "memoria_mediana_avl_mb": memoria_avl
        }

        resultados.append(resultado)

        # Exibe um resumo do cenário.
        print(f"Registros inseridos: {abb_inseridos}")
        print(f"Duplicados: {abb_duplicados}")

        print(f"Tempo ABB: {tempo_abb:.3f} ms")
        print(f"Tempo AVL: {tempo_avl:.3f} ms")

        print(f"Altura ABB: {altura_abb}")
        print(f"Altura AVL: {altura_avl}")
        print(f"Limite AVL: {limite_avl:.2f}")

        print(f"Memória ABB: {memoria_abb:.4f} MB")
        print(f"Memória AVL: {memoria_avl:.4f} MB")

        print("AVL dentro do limite:", altura_avl <= limite_avl)

        print("-" * 55)

    return resultados


def salvar_resultados_csv(resultados):
    """Salva os resultados do benchmark em um arquivo CSV."""

    pasta_resultados = RAIZ / "benchmark"
    pasta_resultados.mkdir(parents=True, exist_ok=True)

    caminho_csv = pasta_resultados / "resultados_benchmark.csv"

    campos = [
        "distribuicao",
        "quantidade_registros",
        "registros_inseridos",
        "duplicados",
        "primeiros_7_registros",
        "tempo_mediano_abb_ms",
        "tempo_mediano_avl_ms",
        "altura_abb",
        "altura_avl",
        "limite_altura_avl",
        "avl_dentro_limite",
        "memoria_mediana_abb_mb",
        "memoria_mediana_avl_mb"
    ]

    with open(caminho_csv, "w", newline="", encoding="utf-8-sig") as arquivo:

        escritor = csv.DictWriter(arquivo, fieldnames=campos)

        escritor.writeheader()

        for resultado in resultados:
            linha = resultado.copy()

            linha["primeiros_7_registros"] = repr(
                linha["primeiros_7_registros"]
            )

            escritor.writerow(linha)

    print("\n=== EXPORTAÇÃO DOS RESULTADOS ===")
    print(f"Arquivo salvo em: {caminho_csv}")


if __name__ == "__main__":

    resultados = executar_benchmark_completo()

    salvar_resultados_csv(resultados)
