from __future__ import annotations

from pathlib import Path
import sys
import duckdb
import pandas as pd

# Permite importar data_loader.py a partir da raiz do projeto
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from data_loader import (  # noqa: E402
    CLASSES_CORREGEDOR,
    classificar_situacao,
    classificar_decisao,
    classificar_unidade,
)

RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
DUCKDB_PATH = PROCESSED_DIR / "pje_tre_ce.duckdb"


def ler_csvs_1g(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Lê os CSVs do 1º Grau, normaliza colunas e retorna um DataFrame único."""
    arquivos = sorted(raw_dir.glob("pje-1o-totalidade-de-processos-autuados*.csv"))
    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum CSV do 1º Grau encontrado em {raw_dir}."
        )

    dfs: list[pd.DataFrame] = []
    for arq in arquivos:
        df = pd.read_csv(arq, sep=";", dtype=str, encoding="utf-8")
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)
    df["DT_AUTUACAO"] = pd.to_datetime(
        df["DT_AUTUACAO"],
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce",
    )
    df["ano"] = df["DT_AUTUACAO"].dt.year.astype("Int64")
    df["mes"] = df["DT_AUTUACAO"].dt.month.astype("Int64")
    df = df.dropna(subset=["ano", "mes"])

    df = df.rename(columns={
        "NR_PROCESSO": "nr_processo",
        "CLASSE_JUDICIAL": "classe",
        "ORGAO_JULGADOR": "orgao",
    })

    return df[["nr_processo", "classe", "orgao", "ano", "mes", "DT_AUTUACAO"]].copy()



def ler_csvs_2g(raw_dir: Path = RAW_DIR, excluir_corregedoria: bool = True) -> pd.DataFrame:
    """Lê os CSVs do 2º Grau, normaliza colunas e retorna um DataFrame único."""
    arquivos = sorted(raw_dir.glob("pje-2o-processos-distribuidos-e-redistribuidos-por-periodo*.csv"))
    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum CSV do 2º Grau encontrado em {raw_dir}."
        )

    dfs: list[pd.DataFrame] = []
    for arq in arquivos:
        df = pd.read_csv(arq, sep=";", dtype=str, encoding="utf-8")
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)
    df["dt_distribuicao"] = pd.to_datetime(
        df["dt_distribuicao"],
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce",
    )
    df["ano"] = df["dt_distribuicao"].dt.year.astype("Int64")
    df["mes"] = df["dt_distribuicao"].dt.month.astype("Int64")
    df = df.dropna(subset=["ano", "mes"])

    df = df.rename(columns={
        "ds_classe_judicial": "classe",
        "ds_orgao_julgador": "orgao",
        "tipo_decisao": "tipo_decisao",
        "tarefas": "tarefas",
        "dt_transito_julgado": "dt_transito",
    })

    for col in ["classe", "orgao", "tipo_decisao", "tarefas", "dt_transito"]:
        if col in df.columns:
            df[col] = df[col].fillna("")

    if excluir_corregedoria:
        mask_orgao = ~df["orgao"].str.lower().str.contains("corregedor", na=False)
        mask_classe = ~df["classe"].isin(CLASSES_CORREGEDOR)
        df = df[mask_orgao & mask_classe].copy()

    return df[[
        "nr_processo",
        "classe",
        "orgao",
        "ano",
        "mes",
        "tipo_decisao",
        "tarefas",
        "dt_transito",
        "dt_distribuicao",
    ]].copy()



def aplicar_regras_classificacao(df_2g: pd.DataFrame) -> pd.DataFrame:
    """Aplica as regras de classificação derivadas ao DataFrame do 2º Grau."""
    df = df_2g.copy()
    df["situacao"] = df["tarefas"].apply(classificar_situacao)
    df["decisao"] = df["tipo_decisao"].apply(classificar_decisao)
    df["unidade"] = df["tarefas"].apply(classificar_unidade)
    return df



def salvar_no_duckdb(df_1g: pd.DataFrame, df_2g: pd.DataFrame, db_path: Path = DUCKDB_PATH) -> None:
    """Salva os DataFrames tratados em tabelas DuckDB."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(db_path))
    try:
        con.register("df_1g", df_1g)
        con.register("df_2g", df_2g)

        con.execute("DROP TABLE IF EXISTS processos_1g")
        con.execute("DROP TABLE IF EXISTS processos_2g")

        con.execute("CREATE TABLE processos_1g AS SELECT * FROM df_1g")
        con.execute("CREATE TABLE processos_2g AS SELECT * FROM df_2g")
    finally:
        con.close()



def main() -> None:
    """Orquestra a ingestão dos CSVs e grava a base analítica em DuckDB."""
    print("[1/4] Lendo CSVs do 1º Grau...")
    df_1g = ler_csvs_1g()

    print("[2/4] Lendo CSVs do 2º Grau...")
    df_2g = ler_csvs_2g(excluir_corregedoria=True)

    print("[3/4] Aplicando regras de classificação...")
    df_2g = aplicar_regras_classificacao(df_2g)

    print("[4/4] Salvando no DuckDB...")
    salvar_no_duckdb(df_1g, df_2g)

    print(f"Base gerada com sucesso em: {DUCKDB_PATH}")
    print(f"1º Grau: {len(df_1g):,} registros".replace(",", "."))
    print(f"2º Grau: {len(df_2g):,} registros".replace(",", "."))


if __name__ == "__main__":
    main()
