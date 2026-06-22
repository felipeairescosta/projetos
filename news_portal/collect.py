#!/usr/bin/env python3
"""
Script de coleta avulsa. Pode ser executado diretamente ou pelo cron.

    python collect.py               # coleta todas as fontes
    python collect.py TSE TRE-SP    # coleta fontes específicas
    python collect.py --list        # lista fontes disponíveis
"""
import sys
import argparse
from scraper import SOURCES, init_db, scrape_source, scrape_all, get_stats

def main():
    parser = argparse.ArgumentParser(description="Coletor de notícias TSE/TRE")
    parser.add_argument("siglas", nargs="*", help="Siglas a coletar (ex: TSE TRE-SP)")
    parser.add_argument("--list", action="store_true", help="Lista fontes disponíveis")
    args = parser.parse_args()

    if args.list:
        for s in SOURCES:
            print(f"  {s['sigla']:12} {s['nome']}")
        return

    init_db()

    if args.siglas:
        siglas_upper = [s.upper() for s in args.siglas]
        sources = [s for s in SOURCES if s["sigla"] in siglas_upper]
        if not sources:
            print("Nenhuma fonte encontrada. Use --list para ver as disponíveis.")
            sys.exit(1)
        for src in sources:
            result = scrape_source(src)
            print(f"[{result['sigla']}] status={result['status']} count={result['count']}")
    else:
        print("Iniciando coleta de todas as fontes…")
        results = scrape_all()
        ok    = sum(1 for r in results if r["status"] == "ok")
        total = sum(r.get("count", 0) for r in results)
        print(f"\nPronto! {ok}/{len(results)} fontes coletadas, {total} novas notícias.")

    stats = get_stats()
    print(f"\nTotal no banco: {stats['total']} notícias")

if __name__ == "__main__":
    main()
