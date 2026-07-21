"""CLI do analisador de contas eleitorais.

Uso:
    python main.py analisar <arquivo.json> [--saida relatorio.md]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.analisador import analisar
from src.ingestao.json_loader import carregar_prestacao_de_json
from src.relatorio import renderizar_markdown


def main() -> None:
    parser = argparse.ArgumentParser(description="Analisador de contas eleitorais (Res.-TSE 23.607/2019)")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    analisar_parser = subparsers.add_parser("analisar", help="Analisa uma prestação de contas em JSON")
    analisar_parser.add_argument("arquivo", help="Caminho do JSON com a prestação de contas")
    analisar_parser.add_argument("--saida", help="Arquivo de saída para o relatório (Markdown). Padrão: stdout")

    args = parser.parse_args()

    if args.comando == "analisar":
        prestacao = carregar_prestacao_de_json(args.arquivo)
        relatorio = analisar(prestacao)
        texto = renderizar_markdown(relatorio)
        if args.saida:
            Path(args.saida).write_text(texto, encoding="utf-8")
            print(f"Relatório salvo em {args.saida}")
        else:
            print(texto)


if __name__ == "__main__":
    main()
