"""
Monitoramento de Fluxo de Tarefas — Dashboard PJe
Análise de tarefas por fluxo, responsável e tempo de execução.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re
import io

st.set_page_config(
    page_title="Monitoramento de Fluxo — PJe",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    [data-testid="stMetricValue"] { font-size: 2rem; }
    h1 { color: #1e3a8a; }
    .status-aberta { color: #f59e0b; font-weight: bold; }
    .status-fechada { color: #10b981; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("📋 Monitoramento de Fluxo de Tarefas")
st.caption("Acompanhamento de tarefas por fluxo, responsável e tempo de execução · PJe TRE-CE")


def parse_duration(dur_str: str) -> float:
    """Converte string de duração '0000d 01h 41m 26s' para minutos."""
    if not dur_str or pd.isna(dur_str):
        return 0.0
    pattern = r"(\d+)d\s+(\d+)h\s+(\d+)m\s+(\d+)s"
    m = re.match(pattern, str(dur_str).strip())
    if not m:
        return 0.0
    d, h, mn, s = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
    return d * 1440 + h * 60 + mn + s / 60


def format_duration(minutes: float) -> str:
    if minutes <= 0:
        return "—"
    d = int(minutes // 1440)
    h = int((minutes % 1440) // 60)
    m = int(minutes % 60)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    parts.append(f"{m}m")
    return " ".join(parts)


def load_csv(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    df.columns = ["fluxo", "tarefa", "inicio", "fim", "responsavel", "duracao", "status"]

    # Remove linha de resumo
    df = df[df["fluxo"] != "Resumo do fluxo"].copy()

    df["inicio_dt"] = pd.to_datetime(df["inicio"], format="%d/%m/%Y, %H:%M:%S", errors="coerce")
    df["fim_dt"] = pd.to_datetime(df["fim"], format="%d/%m/%Y, %H:%M:%S", errors="coerce")
    df["duracao_min"] = df["duracao"].apply(parse_duration)

    # Calcula duração para tarefas abertas (sem fim)
    now = datetime.now()
    mask_aberta = df["status"] == "Aberta"
    df.loc[mask_aberta, "duracao_min"] = df.loc[mask_aberta, "inicio_dt"].apply(
        lambda x: (now - x).total_seconds() / 60 if pd.notna(x) else 0
    )

    df["responsavel"] = df["responsavel"].fillna("(sem responsável)")
    return df


# ========== UPLOAD ==========
st.sidebar.header("📂 Carregar dados")
uploaded = st.sidebar.file_uploader(
    "Selecione o CSV exportado do PJe",
    type=["csv"],
    help="Formato: Fluxo, Tarefa, Início, Fim, Finalizada por, Duração, Status",
)

# Botão para usar dados de exemplo (CSV embutido)
SAMPLE_CSV = """Fluxo,Tarefa,Início tarefa,Fim tarefa,Finalizada por,Duração,Status
Fluxo - Classes Originárias,Verificar e certificar dados do processo com liminar,"28/05/2026, 13:32:29","28/05/2026, 15:13:56",RAIMUNDO LUCIO GONZAGA WANDERLEY,0000d 01h 41m 26s,Fechada
Fluxo - Classes Originárias,Definir procedimento,"28/05/2026, 15:13:56","28/05/2026, 15:14:04",RAIMUNDO LUCIO GONZAGA WANDERLEY,0000d 00h 00m 08s,Fechada
Fluxo - Classes Originárias,Remeter Processo,"28/05/2026, 15:14:04","28/05/2026, 15:14:10",RAIMUNDO LUCIO GONZAGA WANDERLEY,0000d 00h 00m 05s,Fechada
Fluxo - Gabinetes,Realizar triagem urgentes,"28/05/2026, 15:14:11","28/05/2026, 17:24:44",LIGIA VIEIRA DE SA E LOPES,0000d 02h 10m 32s,Fechada
Fluxo - Preparação de ato judicial,Minutar ato,"28/05/2026, 17:24:44","01/06/2026, 12:53:01",LIGIA VIEIRA DE SA E LOPES,0003d 19h 28m 16s,Fechada
Fluxo - Preparação de ato judicial,Assinar ato,"01/06/2026, 12:53:01","02/06/2026, 10:20:06",WILKER MACEDO LIMA,0000d 21h 27m 05s,Fechada
Fluxo - Lançamento de Movimentos,Lançar movimento,"02/06/2026, 10:20:06","02/06/2026, 16:12:25",JENNY DE SOUSA SILVA,0000d 05h 52m 18s,Fechada
Fluxo - Gabinetes,Remeter Processos - Gabinete,"02/06/2026, 16:12:25","02/06/2026, 20:07:21",,0000d 03h 54m 55s,Fechada
Fluxo - Cumprimento de determinação,Analisar determinação - Urgentes,"02/06/2026, 20:07:21","03/06/2026, 07:27:53",,0000d 11h 20m 31s,Fechada
Fluxo - Ato de Comunicação,Escolher tipo,"03/06/2026, 07:27:53","03/06/2026, 07:27:55",FELIPE AIRES COSTA,0000d 00h 00m 02s,Fechada
Fluxo - Ato de Comunicação,Preparar comunicação,"03/06/2026, 07:27:55","03/06/2026, 07:29:03",FELIPE AIRES COSTA,0000d 00h 01m 07s,Fechada
Fluxo - Ato de Comunicação,Visualizar expediente DJE,"03/06/2026, 07:29:04","03/06/2026, 07:29:11",FELIPE AIRES COSTA,0000d 00h 00m 06s,Fechada
Fluxo - Controle de prazos,Processo com prazo em curso,"03/06/2026, 07:29:12","03/06/2026, 07:29:14",FELIPE AIRES COSTA,0000d 00h 00m 02s,Fechada
Fluxo - Controle de prazos,Analisar resposta do expediente,"03/06/2026, 07:29:14","03/06/2026, 07:29:16",FELIPE AIRES COSTA,0000d 00h 00m 02s,Fechada
Fluxo - Cumprimento de determinação,Analisar determinação - Urgentes,"03/06/2026, 07:29:17","03/06/2026, 07:29:21",FELIPE AIRES COSTA,0000d 00h 00m 03s,Fechada
Fluxo - Cumprimento de determinação,Elaborar Documentos,"03/06/2026, 07:29:21","03/06/2026, 14:05:13",CELMA MARIA CARNEIRO GALENO,0000d 06h 35m 52s,Fechada
Fluxo - Cumprimento de determinação,Analisar determinação - Urgentes,"03/06/2026, 14:05:13","09/06/2026, 07:44:31",,0005d 17h 39m 17s,Fechada
Fluxo - Análise de petições avulsas SJD,Analisar Petição Avulsa,"03/06/2026, 14:10:48","11/06/2026, 08:16:20",FELIPE AIRES COSTA,0007d 18h 05m 32s,Fechada
Fluxo - Análise de petições avulsas,Petições não lidas,"03/06/2026, 14:10:48","08/06/2026, 10:14:16",KISSIA FREIRE ALCANTARA BARROS,0004d 20h 03m 28s,Fechada
Fluxo - Análise de petições avulsas,Petições lidas,"08/06/2026, 10:14:16",,,,Aberta
Fluxo - Cumprimento de determinação,Elaborar Documentos,"09/06/2026, 07:44:31","09/06/2026, 07:51:36",FELIPE AIRES COSTA,0000d 00h 07m 05s,Fechada
Fluxo - Cumprimento de determinação,Analisar determinação - Urgentes,"09/06/2026, 07:51:36","09/06/2026, 07:51:42",FELIPE AIRES COSTA,0000d 00h 00m 05s,Fechada
Fluxo - Cumprimento de determinação,Aguardando providências,"09/06/2026, 07:51:42","09/06/2026, 11:08:43",FELIPE AIRES COSTA,0000d 03h 17m 00s,Fechada
Fluxo - Cumprimento de determinação,Analisar determinação - Urgentes,"09/06/2026, 11:08:43","09/06/2026, 11:08:47",FELIPE AIRES COSTA,0000d 00h 00m 04s,Fechada
Fluxo - Cumprimento de determinação,Digitalizar Documentos,"09/06/2026, 11:08:47","09/06/2026, 11:09:11",FELIPE AIRES COSTA,0000d 00h 00m 23s,Fechada
Fluxo - Cumprimento de determinação,Analisar determinação - Urgentes,"09/06/2026, 11:09:11","09/06/2026, 11:11:40",FELIPE AIRES COSTA,0000d 00h 02m 29s,Fechada
Fluxo - Cumprimento de determinação,Aguardando providências,"09/06/2026, 11:11:40","11/06/2026, 07:58:36",FELIPE AIRES COSTA,0001d 20h 46m 55s,Fechada
Fluxo - Cumprimento de determinação,Analisar determinação - Urgentes,"11/06/2026, 07:58:36","11/06/2026, 07:58:39",FELIPE AIRES COSTA,0000d 00h 00m 02s,Fechada
Fluxo - Cumprimento de determinação,Elaborar Documentos,"11/06/2026, 07:58:39","11/06/2026, 08:00:34",FELIPE AIRES COSTA,0000d 00h 01m 54s,Fechada
Fluxo - Cumprimento de determinação,Analisar determinação - Urgentes,"11/06/2026, 08:00:34","11/06/2026, 08:00:38",FELIPE AIRES COSTA,0000d 00h 00m 03s,Fechada
Fluxo - Classes Originárias,Verificar Pendências,"11/06/2026, 08:00:38","11/06/2026, 08:00:41",FELIPE AIRES COSTA,0000d 00h 00m 02s,Fechada
Fluxo - Gabinetes,Realizar triagem urgentes,"11/06/2026, 08:00:42","11/06/2026, 17:40:56",LIGIA VIEIRA DE SA E LOPES,0000d 09h 40m 14s,Fechada
Fluxo - Preparação de ato judicial,Minutar ato,"11/06/2026, 17:40:56","13/06/2026, 13:15:44",LIGIA VIEIRA DE SA E LOPES,0001d 19h 34m 48s,Fechada
Fluxo - Preparação de ato judicial,Assinar ato,"13/06/2026, 13:15:44","14/06/2026, 21:18:54",WILKER MACEDO LIMA,0001d 08h 03m 09s,Fechada
Fluxo - Lançamento de Movimentos,Lançar movimento,"14/06/2026, 21:18:54","15/06/2026, 08:39:08",LIGIA VIEIRA DE SA E LOPES,0000d 11h 20m 13s,Fechada
Fluxo - Gabinetes,Remeter Processos - Gabinete,"15/06/2026, 08:39:09","15/06/2026, 09:03:29",,0000d 00h 24m 20s,Fechada
Fluxo - Cumprimento de determinação,Analisar determinação - Urgentes,"15/06/2026, 09:03:30","15/06/2026, 09:07:44",,0000d 00h 04m 14s,Fechada
Fluxo - Elaboração de documento SJD ao Magistrado,Elaborar documentos - Magistrado Assinar,"15/06/2026, 09:07:44","16/06/2026, 11:12:10",FELIPE AIRES COSTA,0001d 02h 04m 25s,Fechada
Fluxo - Cumprimento de determinação,Analisar determinação - Urgentes,"15/06/2026, 09:07:45","15/06/2026, 09:07:58",FELIPE AIRES COSTA,0000d 00h 00m 12s,Fechada
Fluxo - Cumprimento de determinação,Aguardando providências,"15/06/2026, 09:07:58","16/06/2026, 06:26:52",,0000d 21h 18m 54s,Fechada
Fluxo - Cumprimento de determinação,Analisar determinação - Urgentes,"16/06/2026, 06:26:52","16/06/2026, 06:27:05",FELIPE AIRES COSTA,0000d 00h 00m 12s,Fechada
Fluxo - Ato de Comunicação,Escolher tipo,"16/06/2026, 06:27:05","16/06/2026, 06:27:09",FELIPE AIRES COSTA,0000d 00h 00m 03s,Fechada
Fluxo - Ato de Comunicação,Preparar comunicação,"16/06/2026, 06:27:09","16/06/2026, 06:28:15",FELIPE AIRES COSTA,0000d 00h 01m 05s,Fechada
Fluxo - Ato de Comunicação,Visualizar expediente DJE,"16/06/2026, 06:28:16","16/06/2026, 06:28:21",FELIPE AIRES COSTA,0000d 00h 00m 04s,Fechada
Fluxo - Controle de prazos,Processo com prazo em curso,"16/06/2026, 06:28:21","16/06/2026, 06:28:24",FELIPE AIRES COSTA,0000d 00h 00m 02s,Fechada
Fluxo - Controle de prazos,Analisar resposta do expediente,"16/06/2026, 06:28:24","16/06/2026, 06:28:26",FELIPE AIRES COSTA,0000d 00h 00m 02s,Fechada
Fluxo - Cumprimento de determinação,Analisar determinação - Urgentes,"16/06/2026, 06:28:26","16/06/2026, 06:28:38",FELIPE AIRES COSTA,0000d 00h 00m 11s,Fechada
Fluxo - Cumprimento de determinação,Aguardando providências,"16/06/2026, 06:28:38","25/06/2026, 18:51:11",FELIPE AIRES COSTA,0009d 12h 22m 33s,Fechada
Fluxo - Elaboração de documento SJD ao Magistrado,Assinar Documentos,"16/06/2026, 11:12:10","25/06/2026, 18:36:07",WILKER MACEDO LIMA,0009d 07h 23m 56s,Fechada
Fluxo - Análise de petições avulsas SJD,Analisar Petição Avulsa,"24/06/2026, 14:10:22","25/06/2026, 18:51:29",FELIPE AIRES COSTA,0001d 04h 41m 07s,Fechada
Fluxo - Análise de petições avulsas,Petições não lidas,"24/06/2026, 14:10:22",,,,Aberta
Fluxo - Cumprimento de determinação,Analisar determinação - Urgentes,"25/06/2026, 18:51:12","25/06/2026, 18:51:18",FELIPE AIRES COSTA,0000d 00h 00m 06s,Fechada
Fluxo - Cumprimento de determinação,Elaborar Documentos,"25/06/2026, 18:51:18","26/06/2026, 10:01:55",MARCUS BEZERRA DE MENEZES SERPA,0000d 15h 10m 37s,Fechada
Fluxo - Cumprimento de determinação,Analisar determinação - Urgentes,"26/06/2026, 10:01:55","26/06/2026, 10:05:51",FELIPE AIRES COSTA,0000d 00h 03m 55s,Fechada
Fluxo - Cumprimento de determinação,Aguardando providências,"26/06/2026, 10:05:51",,FELIPE AIRES COSTA,,Aberta
"""

use_sample = st.sidebar.button("Usar dados de exemplo")

if uploaded:
    df = load_csv(uploaded)
elif use_sample:
    df = load_csv(io.StringIO(SAMPLE_CSV))
else:
    st.info("Carregue um CSV exportado do PJe ou clique em **Usar dados de exemplo** na barra lateral.")
    st.stop()

# ========== FILTROS ==========
st.sidebar.markdown("---")
st.sidebar.header("Filtros")

fluxos_disponiveis = sorted(df["fluxo"].unique())
fluxos_selecionados = st.sidebar.multiselect(
    "Fluxo",
    options=fluxos_disponiveis,
    default=fluxos_disponiveis,
)

responsaveis_disponiveis = sorted(df["responsavel"].unique())
responsaveis_selecionados = st.sidebar.multiselect(
    "Responsável",
    options=responsaveis_disponiveis,
    default=responsaveis_disponiveis,
)

status_opcoes = ["Aberta", "Fechada"]
status_selecionados = st.sidebar.multiselect(
    "Status",
    options=status_opcoes,
    default=status_opcoes,
)

df_f = df[
    df["fluxo"].isin(fluxos_selecionados) &
    df["responsavel"].isin(responsaveis_selecionados) &
    df["status"].isin(status_selecionados)
].copy()

# ========== KPIs ==========
total = len(df_f)
abertas = (df_f["status"] == "Aberta").sum()
fechadas = (df_f["status"] == "Fechada").sum()
tempo_medio_min = df_f[df_f["status"] == "Fechada"]["duracao_min"].mean()
tempo_total_min = df_f["duracao_min"].sum()
n_responsaveis = df_f[df_f["responsavel"] != "(sem responsável)"]["responsavel"].nunique()
n_fluxos = df_f["fluxo"].nunique()

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
col1.metric("Total de tarefas", total)
col2.metric("Fechadas", fechadas, f"{fechadas/total*100:.0f}%" if total else "—")
col3.metric("Abertas", abertas, delta_color="inverse", delta=f"{abertas/total*100:.0f}%" if total else "—")
col4.metric("Tempo médio (fechadas)", format_duration(tempo_medio_min))
col5.metric("Tempo total acumulado", format_duration(tempo_total_min))
col6.metric("Responsáveis", n_responsaveis)
col7.metric("Fluxos distintos", n_fluxos)

st.markdown("---")

# ========== TABS ==========
tab_linha, tab_fluxo, tab_resp, tab_gantt, tab_tabela = st.tabs([
    "📈 Linha do Tempo", "📊 Por Fluxo", "👤 Por Responsável", "📅 Gantt", "📋 Tabela"
])

# ---- TAB 1: Linha do tempo ----
with tab_linha:
    st.markdown("#### Tarefas ao longo do tempo")
    df_lt = df_f[df_f["inicio_dt"].notna()].copy()
    df_lt["data"] = df_lt["inicio_dt"].dt.date
    por_dia = df_lt.groupby(["data", "status"]).size().reset_index(name="qtd")

    fig = px.bar(
        por_dia, x="data", y="qtd", color="status",
        color_discrete_map={"Fechada": "#10b981", "Aberta": "#f59e0b"},
        labels={"data": "Data de início", "qtd": "Tarefas", "status": "Status"},
        barmode="stack",
    )
    fig.update_layout(height=380, xaxis_title="Data", yaxis_title="Quantidade de tarefas")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Tempo acumulado por data de início")
    acum = df_lt.groupby("data")["duracao_min"].sum().reset_index()
    acum["duracao_h"] = acum["duracao_min"] / 60
    fig2 = px.area(
        acum, x="data", y="duracao_h",
        labels={"data": "Data", "duracao_h": "Horas totais"},
        color_discrete_sequence=["#3b82f6"],
    )
    fig2.update_layout(height=280)
    st.plotly_chart(fig2, use_container_width=True)

# ---- TAB 2: Por Fluxo ----
with tab_fluxo:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Tarefas por Fluxo")
        fluxo_cnt = df_f["fluxo"].value_counts().reset_index()
        fluxo_cnt.columns = ["fluxo", "qtd"]
        # Limpar nome do fluxo para exibição
        fluxo_cnt["fluxo_curto"] = fluxo_cnt["fluxo"].str.replace("Fluxo - ", "", regex=False)
        fig = px.bar(
            fluxo_cnt, x="qtd", y="fluxo_curto", orientation="h",
            color="qtd", color_continuous_scale="Blues",
            labels={"fluxo_curto": "", "qtd": "Tarefas"},
        )
        fig.update_layout(height=400, yaxis={"categoryorder": "total ascending"},
                          coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("#### Tempo médio por Fluxo (horas)")
        tempo_fluxo = (
            df_f[df_f["status"] == "Fechada"]
            .groupby("fluxo")["duracao_min"]
            .mean()
            .reset_index()
        )
        tempo_fluxo.columns = ["fluxo", "media_min"]
        tempo_fluxo["media_h"] = tempo_fluxo["media_min"] / 60
        tempo_fluxo["fluxo_curto"] = tempo_fluxo["fluxo"].str.replace("Fluxo - ", "", regex=False)
        tempo_fluxo = tempo_fluxo.sort_values("media_h")
        fig = px.bar(
            tempo_fluxo, x="media_h", y="fluxo_curto", orientation="h",
            color="media_h", color_continuous_scale="Oranges",
            labels={"fluxo_curto": "", "media_h": "Horas (média)"},
        )
        fig.update_layout(height=400, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Status por Fluxo")
    status_fluxo = df_f.groupby(["fluxo", "status"]).size().reset_index(name="qtd")
    status_fluxo["fluxo_curto"] = status_fluxo["fluxo"].str.replace("Fluxo - ", "", regex=False)
    fig = px.bar(
        status_fluxo, x="fluxo_curto", y="qtd", color="status",
        color_discrete_map={"Fechada": "#10b981", "Aberta": "#f59e0b"},
        barmode="stack",
        labels={"fluxo_curto": "Fluxo", "qtd": "Tarefas", "status": "Status"},
    )
    fig.update_layout(height=350, xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

# ---- TAB 3: Por Responsável ----
with tab_resp:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Tarefas por Responsável")
        resp_cnt = df_f["responsavel"].value_counts().reset_index()
        resp_cnt.columns = ["responsavel", "qtd"]
        fig = px.bar(
            resp_cnt, x="qtd", y="responsavel", orientation="h",
            color="qtd", color_continuous_scale="Purples",
            labels={"responsavel": "", "qtd": "Tarefas"},
        )
        fig.update_layout(height=400, yaxis={"categoryorder": "total ascending"},
                          coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("#### Tempo total por Responsável (horas)")
        tempo_resp = (
            df_f[df_f["responsavel"] != "(sem responsável)"]
            .groupby("responsavel")["duracao_min"]
            .sum()
            .reset_index()
        )
        tempo_resp.columns = ["responsavel", "total_min"]
        tempo_resp["total_h"] = tempo_resp["total_min"] / 60
        tempo_resp = tempo_resp.sort_values("total_h")
        fig = px.bar(
            tempo_resp, x="total_h", y="responsavel", orientation="h",
            color="total_h", color_continuous_scale="Teal",
            labels={"responsavel": "", "total_h": "Horas (total)"},
        )
        fig.update_layout(height=400, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Distribuição de participação")
    col_pie1, col_pie2 = st.columns(2)
    with col_pie1:
        st.markdown("**Por quantidade de tarefas**")
        fig = px.pie(
            resp_cnt[resp_cnt["responsavel"] != "(sem responsável)"],
            values="qtd", names="responsavel", hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig.update_layout(height=320)
        st.plotly_chart(fig, use_container_width=True)
    with col_pie2:
        st.markdown("**Por tempo total dedicado**")
        fig = px.pie(
            tempo_resp, values="total_h", names="responsavel", hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(height=320)
        st.plotly_chart(fig, use_container_width=True)

# ---- TAB 4: Gantt ----
with tab_gantt:
    st.markdown("#### Linha do tempo das tarefas (Gantt)")
    df_g = df_f[df_f["inicio_dt"].notna()].copy()
    df_g["fim_display"] = df_g.apply(
        lambda r: r["fim_dt"] if pd.notna(r["fim_dt"]) else datetime.now(),
        axis=1
    )
    df_g["label"] = df_g["fluxo"].str.replace("Fluxo - ", "", regex=False) + " · " + df_g["tarefa"]
    df_g["cor"] = df_g["status"].map({"Fechada": "#10b981", "Aberta": "#f59e0b"})

    fig = px.timeline(
        df_g,
        x_start="inicio_dt",
        x_end="fim_display",
        y="label",
        color="status",
        color_discrete_map={"Fechada": "#10b981", "Aberta": "#f59e0b"},
        hover_data=["responsavel", "duracao"],
        labels={"label": "Tarefa", "status": "Status"},
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=max(500, len(df_g) * 22), xaxis_title="Data")
    st.plotly_chart(fig, use_container_width=True)

# ---- TAB 5: Tabela ----
with tab_tabela:
    st.markdown("#### Todas as tarefas")
    df_show = df_f[["fluxo", "tarefa", "inicio", "fim", "responsavel", "duracao", "status"]].copy()
    df_show.columns = ["Fluxo", "Tarefa", "Início", "Fim", "Responsável", "Duração", "Status"]
    df_show["Fluxo"] = df_show["Fluxo"].str.replace("Fluxo - ", "", regex=False)

    st.dataframe(
        df_show,
        use_container_width=True,
        height=500,
        column_config={
            "Status": st.column_config.TextColumn(
                "Status",
                help="Aberta = em andamento · Fechada = concluída",
            )
        }
    )

    csv_export = df_show.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Baixar tabela filtrada (.csv)",
        data=csv_export,
        file_name="tarefas_fluxo_filtradas.csv",
        mime="text/csv",
    )

st.markdown("---")
st.caption("Monitoramento de Fluxo · Dashboard PJe · TRE-CE")
