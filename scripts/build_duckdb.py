from __future__ import annotations

from pathlib import Path
import sys
import duckdb
import pandas as pd

# Importar do projeto
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from data_loader import (
    DATA_DIR,
    CLASSES_CORREGEDOR,
    _garantir_csvs_disponiveis,
    classificar_situacao,
    classificar_decisao,
    classificar_unidade,
)

CACHE_DIR = DATA_DIR
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
DUCKDB_PATH = PROCESSED_DIR / "pje_tre_ce.duckdb"


def ler_csvs_1g() -> pd.DataFrame:
    _garantir_csvs_disponiveis()

    arquivos = sorted(CACHE_DIR.glob("pje-1o-totalidade-de-processos-autuados*.csv"))
    if not arquivos:
        raise FileNotFoundError("CSV 1º Grau não encontrado.")

    dfs = [pd.read_csv(arq, sep=";", dtype=str, encoding="utf-8") for arq in arquivos]
    df = pd.concat(dfs, ignore_index=True)

    df["DT_AUTUACAO"] = pd.to_datetime(
        df["DT_AUTUACAO"],
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce",
    )

    df["ano"] = df["DT_AUTUACAO"].dt.year
    df["mes"] = df["DT_AUTUACAO"].dt.month
    df = df.dropna(subset=["ano", "mes"])

    df = df.rename(columns={
        "NR_PROCESSO": "nr_processo",
        "CLASSE_JUDICIAL": "classe",
        "ORGAO_JULGADOR": "orgao",
    })

    return df[["nr_processo", "classe", "orgao", "ano", "mes", "DT_AUTUACAO"]]


def ler_csvs_2g(excluir_corregedoria: bool = True) -> pd.DataFrame:
    _garantir_csvs_disponiveis()

    arquivos = sorted(CACHE_DIR.glob("pje-2o-processos-distribuidos-e-redistribuidos-por-periodo*.csv"))
    if not arquivos:
        raise FileNotFoundError("CSV 2º Grau não encontrado.")

    dfs = [pd.read_csv(arq, sep=";", dtype=str, encoding="utf-8") for arq in arquivos]
    df = pd.concat(dfs, ignore_index=True)

    df["dt_distribuicao"] = pd.to_datetime(
        df["dt_distribuicao"],
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce",
    )

    df["ano"] = df["dt_distribuicao"].dt.year
    df["mes"] = df["dt_distribuicao"].dt.month
    df = df.dropna(subset=["ano", "mes"])

    df = df.rename(columns={
        "ds_classe_judicial": "classe",
        "ds_orgao_julgador": "orgao",
        "tipo_decisao": "tipo_decisao",
        "tarefas": "tarefas",
        "dt_transito_julgado": "dt_transito",
    })

    for col in ["classe", "orgao", "tipo_decisao", "tarefas"]:
        if col in df.columns:
            df[col] = df[col].fillna("")

    if excluir_corregedoria:
        mask_orgao = ~df["orgao"].str.lower().str.contains("corregedor", na=False)
        mask_classe = ~df["classe"].isin(CLASSES_CORREGEDOR)
        df = df[mask_orgao & mask_classe]

    return df[[
        "nr_processo",
        "classe",
        "orgao",
        "ano",
        "mes",
        "tipo_decisao",
        "tarefas",
        "dt_transito",
        "dt_distribuicao"
    ]]


def aplicar_regras_classificacao(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["situacao"] = df["tarefas"].apply(classificar_situacao)
    df["decisao"] = df["tipo_decisao"].apply(classificar_decisao)
    df["unidade"] = df["tarefas"].apply(classificar_unidade)
    return df


def salvar_no_duckdb(df_1g: pd.DataFrame, df_2g: pd.DataFrame) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DUCKDB_PATH))
    try:
        con.execute("DROP TABLE IF EXISTS processos_1g")
        con.execute("DROP TABLE IF EXISTS processos_2g")

        con.register("df1", df_1g)
        con.register("df2", df_2g)

        con.execute("CREATE TABLE processos_1g AS SELECT * FROM df1")
        con.execute("CREATE TABLE processos_2g AS SELECT * FROM df2")
    finally:
        con.close()


def main() -> None:
    print("Baixando dados do Google Drive, se necessário...")
    _garantir_csvs_disponiveis()

    print("Lendo 1º Grau...")
    df_1g = ler_csvs_1g()

    print("Lendo 2º Grau...")
    df_2g = ler_csvs_2g(excluir_corregedoria=True)

    print("Classificando dados...")
    df_2g = aplicar_regras_classificacao(df_2g)

    print("Salvando no DuckDB...")
    salvar_no_duckdb(df_1g, df_2g)

    print("Concluído com sucesso.")
    print(f"Banco gerado em: {DUCKDB_PATH}")
    print(f"1º Grau: {len(df_1g):,}".replace(",", "."))
    print(f"2º Grau: {len(df_2g):,}".replace(",", "."))


if __name__ == "__main__":
    main()
