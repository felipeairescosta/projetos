"""
Módulo de carregamento e processamento de dados do PJe — TRE-CE.

Responsável por ler os CSVs brutos do 1º e 2º Grau, aplicar filtros
(ex: exclusão de processos da Corregedoria) e retornar DataFrames
prontos para uso no dashboard.
"""

from pathlib import Path
import pandas as pd
import streamlit as st

# Pasta onde ficam os CSVs do PJe
DATA_DIR = Path(__file__).parent / "data"

# Classes processuais de competência do Corregedor (excluídas do 2G)
CLASSES_CORREGEDOR = {
    "CORREIÇÃO ORDINÁRIA",
    "CORREIÇÃO",
    "INSPEÇÃO",
    "REVISÃO DE ELEITORADO",
    "DUPLICIDADE/PLURALIDADE DE INSCRIÇÕES - COINCIDÊNCIAS",
    "COINCIDÊNCIA",
    "REGULARIZAÇÃO DE SITUAÇÃO DO ELEITOR",
    "REGULARIZAÇÃO DE SITUAÇÃO DE ELEITOR",
    "DIREITOS POLÍTICOS",
    "PETIÇÃO CORREGEDORIA",
    "RECLAMAÇÃO DISCIPLINAR",
    "CRIAÇÃO DE ZONA ELEITORAL OU REMANEJAMENTO",
}


@st.cache_data
def load_1g() -> pd.DataFrame:
    """Carrega todos os CSVs do 1º Grau e retorna um DataFrame único."""
    arquivos = sorted(DATA_DIR.glob("pje-1o-totalidade-de-processos-autuados*.csv"))
    dfs = []
    for arq in arquivos:
        df = pd.read_csv(arq, sep=";", dtype=str, encoding="utf-8")
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)

    # Converter data de autuação para datetime e extrair ano/mês
    df["DT_AUTUACAO"] = pd.to_datetime(df["DT_AUTUACAO"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
    df["ano"] = df["DT_AUTUACAO"].dt.year.astype("Int64")
    df["mes"] = df["DT_AUTUACAO"].dt.month.astype("Int64")

    # Remover linhas sem data válida
    df = df.dropna(subset=["ano", "mes"])

    # Padronizar nomes de colunas (mais amigável para uso)
    df = df.rename(columns={
        "NR_PROCESSO": "nr_processo",
        "CLASSE_JUDICIAL": "classe",
        "ORGAO_JULGADOR": "orgao",
    })

    return df[["nr_processo", "classe", "orgao", "ano", "mes", "DT_AUTUACAO"]]


@st.cache_data
def load_2g(excluir_corregedoria: bool = True) -> pd.DataFrame:
    """
    Carrega todos os CSVs do 2º Grau.

    Por padrão exclui processos de competência do Corregedor,
    tanto pelo órgão julgador quanto pelas classes processuais.
    """
    arquivos = sorted(DATA_DIR.glob("pje-2o-processos-distribuidos-e-redistribuidos-por-periodo*.csv"))
    dfs = []
    for arq in arquivos:
        df = pd.read_csv(arq, sep=";", dtype=str, encoding="utf-8")
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)

    # Converter data de distribuição
    df["dt_distribuicao"] = pd.to_datetime(df["dt_distribuicao"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
    df["ano"] = df["dt_distribuicao"].dt.year.astype("Int64")
    df["mes"] = df["dt_distribuicao"].dt.month.astype("Int64")
    df = df.dropna(subset=["ano", "mes"])

    # Renomear para nomes mais curtos e consistentes com o 1G
    df = df.rename(columns={
        "ds_classe_judicial": "classe",
        "ds_orgao_julgador": "orgao",
        "tipo_decisao": "tipo_decisao",
        "tarefas": "tarefas",
        "dt_transito_julgado": "dt_transito",
    })

    # Preencher NaN em colunas de texto com string vazia (facilita filtros)
    for col in ["classe", "orgao", "tipo_decisao", "tarefas", "dt_transito"]:
        if col in df.columns:
            df[col] = df[col].fillna("")

    # Filtro da Corregedoria
    if excluir_corregedoria:
        mask_orgao = ~df["orgao"].str.lower().str.contains("corregedor", na=False)
        mask_classe = ~df["classe"].isin(CLASSES_CORREGEDOR)
        df = df[mask_orgao & mask_classe].copy()

    return df[["nr_processo", "classe", "orgao", "ano", "mes",
               "tipo_decisao", "tarefas", "dt_transito", "dt_distribuicao"]]


def classificar_situacao(tarefas: str) -> str:
    """Classifica o processo em uma situação atual com base no campo 'tarefas'."""
    if not tarefas:
        return "Sem informação"
    t = tarefas
    if "Arquivado" in t or "arquivado" in t:
        return "Arquivado"
    if "Expedido" in t or "Devolvido" in t or "remetido" in t or "Origem" in t:
        return "Expedido/Devolvido"
    if "Aguardando" in t:
        return "Aguardando"
    return "Em tramitação"


def classificar_decisao(tipo: str) -> str:
    """Classifica o tipo de decisão em categoria amigável."""
    if tipo == "DECISÃO COLEGIADA":
        return "Decisão Colegiada"
    if tipo == "DECISÃO MONOCRÁTICA":
        return "Decisão Monocrática"
    return "Sem decisão"


# Mapeamento tarefa -> unidade organizacional (CPROC / ASSESSORIA / OUTRAS)
# Baseado na classificação que já construímos no dashboard HTML
REGRAS_UNIDADE = [
    # CPROC — cartório
    ("Manter Processo Arquivado", "CPROC"),
    ("Manter Processos Expedidos", "CPROC"),
    ("Manter Processos Devolvidos a Origem", "CPROC"),
    ("Manter Processos Suspensos ou Sobrestados", "CPROC"),
    ("Manter processos arquivados provisoriamente", "CPROC"),
    ("Manter recurso arquivado", "CPROC"),
    ("Processos remetidos ao TSE", "CPROC"),
    ("Processos remetidos à zona", "CPROC"),
    ("Processos Expedidos a Origem", "CPROC"),
    ("Aguardando apreciação de outra instância", "CPROC"),
    ("Aguardando apreciação pela instância superior", "CPROC"),
    ("Aguardando julgamento do recurso interno", "CPROC"),
    ("Aguardando providências", "CPROC"),
    ("Processo com prazo em curso", "CPROC"),
    ("Verificar Pendências", "CPROC"),
    ("Verificar e Certificar dados do processo", "CPROC"),
    ("Visualizar expediente DJE", "CPROC"),
    ("Analisar determinação", "CPROC"),
    ("Analisar petição avulsa de autuação", "CPROC"),
    ("Analisar resposta do expediente", "CPROC"),
    ("Analisar Processos", "CPROC"),
    ("Elaborar Documentos", "CPROC"),
    ("Preparar comunicação", "CPROC"),
    ("Desentranhar documentos", "CPROC"),
    ("Deslocar relator Vista", "CPROC"),
    ("Escolher tipo", "CPROC"),
    # ASSESSORIA — gabinetes
    ("Minutar Relatório, Voto e Ementa", "ASSESSORIA"),
    ("Conferir Relatório, Voto e Ementa", "ASSESSORIA"),
    ("Revisar Relatório, Voto e Ementa", "ASSESSORIA"),
    ("Iniciar Acórdão - SJD", "ASSESSORIA"),
    ("Analisar Acórdão Assinado - SJD", "ASSESSORIA"),
    ("Assinar acórdão ou resolução", "ASSESSORIA"),
    ("Assinar Documentos", "ASSESSORIA"),
    ("Assinar ato", "ASSESSORIA"),
    ("Minutar ato", "ASSESSORIA"),
    ("Revisar ato", "ASSESSORIA"),
    ("Lançar movimento", "ASSESSORIA"),
    ("Lançar movimentos de Julgamento Colegiado", "ASSESSORIA"),
    ("Realizar triagem ordinários", "ASSESSORIA"),
    ("Realizar triagem urgentes", "ASSESSORIA"),
    ("Aguarda Julgamento - incluído em pauta virtual", "ASSESSORIA"),
    ("Aguarda Julgamento - incluído em pauta - vista", "ASSESSORIA"),
    ("Aguarda Julgamento - incluído em pauta", "ASSESSORIA"),
    ("Aguarda Sessão de Julgamento Virtual", "ASSESSORIA"),
    ("Aguarda Sessão de Julgamento", "ASSESSORIA"),
    ("Incluído em pauta", "ASSESSORIA"),
    ("Elaborar voto vista", "ASSESSORIA"),
    ("Analisar Petição Avulsa", "ASSESSORIA"),
    ("Analisar Petição em processo arquivado", "ASSESSORIA"),
    ("Petições descartadas", "ASSESSORIA"),
    ("Petições lidas", "ASSESSORIA"),
    ("Petições não lidas", "ASSESSORIA"),
    # OUTRAS — ASEPA, Corregedoria residual
    ("Analisar Processo - ASEPA", "OUTRAS"),
    ("Analisar Processo - Corregedoria", "OUTRAS"),
    ("Processo Corregedoria", "OUTRAS"),
    ("- Corregedoria", "OUTRAS"),
]


def classificar_unidade(tarefas: str) -> str:
    """Classifica o processo na unidade organizacional responsável."""
    if not tarefas:
        return "SEM TAREFA"
    # Verifica correspondência exata primeiro
    for chave, unidade in REGRAS_UNIDADE:
        if tarefas == chave:
            return unidade
    # Depois correspondência parcial
    for chave, unidade in REGRAS_UNIDADE:
        if chave in tarefas:
            return unidade
    return "SEM CLASSIFICAÇÃO"
