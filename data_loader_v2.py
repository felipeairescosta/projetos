"""
Loader v2 para o Dashboard PJe — TRE-CE.

Prioriza leitura a partir do banco DuckDB gerado em data/processed/pje_tre_ce.duckdb.
Se o banco ainda não existir, faz fallback para o fluxo atual com CSVs locais/
Google Drive, preservando compatibilidade com o projeto original.
"""

from __future__ import annotations

from pathlib import Path
import duckdb
import pandas as pd
import streamlit as st

from data_loader import (
    DATA_DIR,
    GDRIVE_FOLDER_ID,
    CLASSES_CORREGEDOR,
    REGRAS_UNIDADE,
    _baixar_csvs_do_drive,
    _garantir_csvs_disponiveis,
    classificar_situacao,
    classificar_decisao,
    classificar_unidade,
)

ROOT_DIR = Path(__file__).parent
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
DUCKDB_PATH = PROCESSED_DIR / "pje_tre_ce.duckdb"


def duckdb_disponivel() -> bool:
    """Retorna True se o banco analítico já existir."""
    return DUCKDB_PATH.exists()


def _query_duckdb(sql: str, params: list | None = None) -> pd.DataFrame:
    """Executa uma consulta no DuckDB e retorna DataFrame."""
    con = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    try:
        if params:
            return con.execute(sql, params).df()
        return con.execute(sql).df()
    finally:
        con.close()


@st.cache_data
def load_1g() -> pd.DataFrame:
    """
    Carrega os dados do 1º Grau.

    Prioridade:
    1. DuckDB, se disponível.
    2. Fallback para o fluxo atual com CSV.
    """
    if duckdb_disponivel():
        return _query_duckdb(
            """
            SELECT nr_processo, classe, orgao, ano, mes, DT_AUTUACAO
            FROM processos_1g
            """
        )

    # Fallback para o comportamento atual
    _garantir_csvs_disponiveis()

    arquivos = sorted(DATA_DIR.glob("pje-1o-totalidade-de-processos-autuados*.csv"))
    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum CSV do 1º Grau encontrado em {DATA_DIR}. "
            "Verifique se o download do Google Drive foi bem-sucedido."
        )

    dfs = []
    for arq in arquivos:
        df = pd.read_csv(arq, sep=";", dtype=str, encoding="utf-8")
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)

    df["DT_AUTUACAO"] = pd.to_datetime(df["DT_AUTUACAO"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
    df["ano"] = df["DT_AUTUACAO"].dt.year.astype("Int64")
    df["mes"] = df["DT_AUTUACAO"].dt.month.astype("Int64")
    df = df.dropna(subset=["ano", "mes"])

    df = df.rename(columns={
        "NR_PROCESSO": "nr_processo",
        "CLASSE_JUDICIAL": "classe",
        "ORGAO_JULGADOR": "orgao",
    })

    return df[["nr_processo", "classe", "orgao", "ano", "mes", "DT_AUTUACAO"]]


@st.cache_data
def load_2g(excluir_corregedoria: bool = True) -> pd.DataFrame:
    """
    Carrega os dados do 2º Grau.

    Prioridade:
    1. DuckDB, se disponível.
    2. Fallback para o fluxo atual com CSV.
    """
    if duckdb_disponivel():
        df = _query_duckdb(
            """
            SELECT nr_processo, classe, orgao, ano, mes,
                   tipo_decisao, tarefas, dt_transito, dt_distribuicao,
                   situacao, decisao, unidade
            FROM processos_2g
            """
        )
        if excluir_corregedoria:
            mask_orgao = ~df["orgao"].str.lower().str.contains("corregedor", na=False)
            mask_classe = ~df["classe"].isin(CLASSES_CORREGEDOR)
            df = df[mask_orgao & mask_classe].copy()
        return df

    # Fallback para o comportamento atual
    _garantir_csvs_disponiveis()

    arquivos = sorted(DATA_DIR.glob("pje-2o-processos-distribuidos-e-redistribuidos-por-periodo*.csv"))
    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum CSV do 2º Grau encontrado em {DATA_DIR}. "
            "Verifique se o download do Google Drive foi bem-sucedido."
        )

    dfs = []
    for arq in arquivos:
        df = pd.read_csv(arq, sep=";", dtype=str, encoding="utf-8")
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)

    df["dt_distribuicao"] = pd.to_datetime(df["dt_distribuicao"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
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

    df["situacao"] = df["tarefas"].apply(classificar_situacao)
    df["decisao"] = df["tipo_decisao"].apply(classificar_decisao)
    df["unidade"] = df["tarefas"].apply(classificar_unidade)

    return df[[
        "nr_processo", "classe", "orgao", "ano", "mes",
        "tipo_decisao", "tarefas", "dt_transito", "dt_distribuicao",
        "situacao", "decisao", "unidade"
    ]]


__all__ = [
    "DATA_DIR",
    "GDRIVE_FOLDER_ID",
    "CLASSES_CORREGEDOR",
    "REGRAS_UNIDADE",
    "DUCKDB_PATH",
    "duckdb_disponivel",
    "load_1g",
    "load_2g",
    "classificar_situacao",
    "classificar_decisao",
    "classificar_unidade",
    "_baixar_csvs_do_drive",
    "_garantir_csvs_disponiveis",
]
