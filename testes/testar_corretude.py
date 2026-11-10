from pathlib import Path
import subprocess
import sys

RAIZ = Path(__file__).resolve().parents[1]
CARGAS = RAIZ / "cargas"
PROGRAMAS = [
    ("Fase 2 - ABB", RAIZ / "fase2" / "systemaf2.py", CARGAS / "pequeno_esperado_fase1.txt"),
    ("Fase 3 - AVL", RAIZ / "fase3" / "systemaf3.py", CARGAS / "pequeno_esperado_fase3.txt"),
]


def executar_teste(nome, programa, entrada, esperado):
    processo = subprocess.run(
        [sys.executable, str(programa), str(entrada)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    if processo.returncode != 0:
        print(f"[ERRO] {nome}: programa terminou com código {processo.returncode}")
        if processo.stderr:
            print(processo.stderr.strip())
        return False

    linhas_obtidas = processo.stdout.splitlines()
    linhas_esperadas = esperado.read_text(encoding="utf-8").splitlines()

    if linhas_obtidas == linhas_esperadas:
        tempo = next(
            (linha for linha in processo.stderr.splitlines() if linha.startswith("TEMPO_MS")),
            "tempo não informado",
        )
        print(f"[OK] {nome}: {len(linhas_esperadas)} linhas conferidas. {tempo}")
        return True

    print(f"[FALHOU] {nome}: saída diferente do arquivo esperado.")
    limite = min(len(linhas_obtidas), len(linhas_esperadas))
    for i in range(limite):
        if linhas_obtidas[i] != linhas_esperadas[i]:
            print(f"  Primeira diferença na linha {i + 1}:")
            print(f"  Esperado: {linhas_esperadas[i]!r}")
            print(f"  Obtido:   {linhas_obtidas[i]!r}")
            break
    else:
        print(f"  Quantidade esperada: {len(linhas_esperadas)}")
        print(f"  Quantidade obtida:  {len(linhas_obtidas)}")
    return False

def main():
    entrada = CARGAS / "pequeno.txt"
    if not entrada.exists():
        print(f"Arquivo de entrada não encontrado: {entrada}")
        raise SystemExit(1)

    resultados = [
        executar_teste(nome, programa, entrada, esperado)
        for nome, programa, esperado in PROGRAMAS
    ]

    aprovados = sum(resultados)
    print(f"\nResultado: {aprovados}/{len(resultados)} testes aprovados.")
    raise SystemExit(0 if aprovados == len(resultados) else 1)


if __name__ == "__main__":
    main()