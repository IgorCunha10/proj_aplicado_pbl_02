
from pathlib import Path
import sys

# Caminho da raiz do projeto
RAIZ = Path(__file__).resolve().parent.parent

# Permite importar os módulos das fases 2 e 3
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


if __name__ == "__main__":
    testar_leitura_cargas()
