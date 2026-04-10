"""
Dashboard PJe — TRE-CE
Análise de processos distribuídos no 1º e 2º Grau.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from data_loader import (
    load_1g,
    load_2g,
    classificar_situacao,
    classificar_decisao,
    classificar_unidade,
)

# ========== CONFIGURAÇÃO DA PÁGINA ==========
st.set_page_config(
    page_title="Dashboard PJe — TRE-CE",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS para ajustar um pouco o visual
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    [data-testid="stMetricValue"] { font-size: 2rem; }
    h1 { color: #1e3a8a; }
    </style>
""", unsafe_allow_html=True)

# ========== TÍTULO ==========
st.title("⚖️ Dashboard PJe — TRE-CE")
st.caption("Análise de processos distribuídos no 1º e 2º Grau · Tribunal Regional Eleitoral do Ceará")

# ========== CARREGAMENTO DOS DADOS ==========
with st.spinner("Carregando dados do PJe..."):
    df_1g = load_1g()
    df_2g = load_2g(excluir_corregedoria=True)

# Enriquecer o 2G com classificações derivadas
df_2g["situacao"] = df_2g["tarefas"].apply(classificar_situacao)
df_2g["decisao"] = df_2g["tipo_decisao"].apply(classificar_decisao)
df_2g["unidade"] = df_2g["tarefas"].apply(classificar_unidade)

# ========== TABS ==========
tab1, tab2 = st.tabs(["1º Grau", "2º Grau"])

with tab1:
    grau = "1º Grau"
    df = df_1g
    # Filtros
    st.markdown("### Filtros")
    col_filt1, col_filt2 = st.columns(2)
    with col_filt1:
        anos_disponiveis = sorted(df["ano"].dropna().unique().tolist())
        ano_selecionado = st.selectbox(
            "Ano",
            options=["Todos"] + [str(a) for a in anos_disponiveis],
            index=0,
            key="ano_1g"
        )
    with col_filt2:
        orgao_selecionado = "Todos"
        if ano_selecionado != "Todos":
            df_temp = df[df["ano"] == int(ano_selecionado)].copy()
            orgaos_disponiveis = sorted(df_temp["orgao"].dropna().unique().tolist())
            orgao_selecionado = st.selectbox(
                "Órgão julgador",
                options=["Todos"] + orgaos_disponiveis,
                index=0,
                key="orgao_1g"
            )
    
    # Filtros de data (aparecem apenas quando ano específico é selecionado)
    dt_inicial = None
    dt_final = None
    if ano_selecionado != "Todos":
        col_filt3, col_filt4 = st.columns(2)
        df_ano = df[df["ano"] == int(ano_selecionado)].copy()
        data_min = df_ano["DT_AUTUACAO"].min().date()
        data_max = df_ano["DT_AUTUACAO"].max().date()
        
        # Limitar calendário ao ano selecionado
        ano_int = int(ano_selecionado)
        min_date_ano = pd.to_datetime(f"{ano_int}-01-01").date()
        max_date_ano = pd.to_datetime(f"{ano_int}-12-31").date()
        
        with col_filt3:
            dt_inicial = st.date_input(
                "Data inicial",
                value=data_min,
                min_value=min_date_ano,
                max_value=max_date_ano,
                format="DD/MM/YYYY",
                key="dt_inicial_1g"
            )
        with col_filt4:
            dt_final = st.date_input(
                "Data final",
                value=data_max,
                min_value=min_date_ano,
                max_value=max_date_ano,
                format="DD/MM/YYYY",
                key="dt_final_1g"
            )
    
    if ano_selecionado != "Todos":
        df_filtrado = df[df["ano"] == int(ano_selecionado)].copy()
        if orgao_selecionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado["orgao"] == orgao_selecionado]
        if dt_inicial and dt_final:
            df_filtrado = df_filtrado[
                (df_filtrado["DT_AUTUACAO"].dt.date >= dt_inicial) &
                (df_filtrado["DT_AUTUACAO"].dt.date <= dt_final)
            ]
    else:
        df_filtrado = df.copy()
    st.caption(
        f"**Total carregado:** {len(df):,} processos".replace(",", ".")
    )
    st.caption(
        f"**Após filtros:** {len(df_filtrado):,} processos".replace(",", ".")
    )
    # ========== KPIs ==========
    st.markdown("### 📊 Indicadores")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de processos", f"{len(df_filtrado):,}".replace(",", "."))
    col2.metric("Classes distintas", df_filtrado["classe"].nunique())
    col3.metric("Órgãos julgadores", df_filtrado["orgao"].nunique())
    col4.metric("Período", f"{df_filtrado['ano'].min()}–{df_filtrado['ano'].max()}")
    st.markdown("---")
    # ========== GRÁFICOS ==========
    # Gráfico 1: Distribuição temporal (ano ou mês)
    col_esq, col_dir = st.columns(2)
    with col_esq:
        if ano_selecionado == "Todos":
            st.markdown("#### Processos por Ano")
            por_ano = df_filtrado.groupby("ano").size().reset_index(name="qtd")
            fig = px.bar(
                por_ano, x="ano", y="qtd",
                labels={"ano": "Ano", "qtd": "Quantidade"},
                color_discrete_sequence=["#3b82f6"],
            )
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(f"#### Processos por Mês — {ano_selecionado}")
            por_mes = df_filtrado.groupby("mes").size().reset_index(name="qtd")
            nomes_meses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
            por_mes["mes_nome"] = por_mes["mes"].apply(lambda m: nomes_meses[int(m)-1])
            fig = px.bar(
                por_mes, x="mes_nome", y="qtd",
                labels={"mes_nome": "Mês", "qtd": "Quantidade"},
                color_discrete_sequence=["#3b82f6"],
            )
            fig.update_layout(showlegend=False, height=350,
                              xaxis={"categoryorder":"array", "categoryarray": nomes_meses})
            st.plotly_chart(fig, use_container_width=True)
    with col_dir:
        st.markdown("#### Top 10 Classes Processuais")
        top_classes = df_filtrado["classe"].value_counts().head(10).reset_index()
        top_classes.columns = ["classe", "qtd"]
        fig = px.bar(
            top_classes, x="qtd", y="classe", orientation="h",
            labels={"classe": "", "qtd": "Quantidade"},
            color_discrete_sequence=["#6366f1"],
        )
        fig.update_layout(showlegend=False, height=350,
                          yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(fig, use_container_width=True)
    # ========== TABELA DE ÓRGÃOS JULGADORES ==========
    st.markdown("---")
    st.markdown("#### Top 15 Órgãos Julgadores")
    top_orgaos = df_filtrado["orgao"].value_counts().head(15).reset_index()
    top_orgaos.columns = ["Órgão Julgador", "Quantidade"]
    top_orgaos.index = top_orgaos.index + 1
    st.dataframe(top_orgaos, use_container_width=True, height=400)

with tab2:
    grau = "2º Grau"
    df = df_2g
    # Filtros
    st.markdown("### Filtros")
    col_filt1, col_filt2, col_filt3 = st.columns(3)
    with col_filt1:
        anos_disponiveis = sorted(df["ano"].dropna().unique().tolist())
        ano_selecionado = st.selectbox(
            "Ano",
            options=["Todos"] + [str(a) for a in anos_disponiveis],
            index=0,
            key="ano_2g"
        )
    df_temp = df.copy()
    if ano_selecionado != "Todos":
        df_temp = df[df["ano"] == int(ano_selecionado)].copy()
    with col_filt2:
        orgao_selecionado = "Todos"
        if ano_selecionado != "Todos":
            orgaos_disponiveis = sorted(df_temp["orgao"].dropna().unique().tolist())
            orgao_selecionado = st.selectbox(
                "Órgão julgador",
                options=["Todos"] + orgaos_disponiveis,
                index=0,
                key="orgao_2g"
            )
    with col_filt3:
        classes_disponiveis = sorted(df_temp["classe"].dropna().unique().tolist())
        classe_selecionada = st.selectbox(
            "Classe",
            options=["Todos"] + classes_disponiveis,
            index=0,
            key="classe_2g"
        )
    
    # Filtros de data (aparecem apenas quando ano específico é selecionado)
    dt_inicial = None
    dt_final = None
    if ano_selecionado != "Todos":
        col_filt4, col_filt5 = st.columns(2)
        df_ano = df[df["ano"] == int(ano_selecionado)].copy()
        data_min = df_ano["dt_distribuicao"].min().date()
        data_max = df_ano["dt_distribuicao"].max().date()
        
        # Limitar calendário ao ano selecionado
        ano_int = int(ano_selecionado)
        min_date_ano = pd.to_datetime(f"{ano_int}-01-01").date()
        max_date_ano = pd.to_datetime(f"{ano_int}-12-31").date()
        
        with col_filt4:
            dt_inicial = st.date_input(
                "Data inicial",
                value=data_min,
                min_value=min_date_ano,
                max_value=max_date_ano,
                format="DD/MM/YYYY",
                key="dt_inicial_2g"
            )
        with col_filt5:
            dt_final = st.date_input(
                "Data final",
                value=data_max,
                min_value=min_date_ano,
                max_value=max_date_ano,
                format="DD/MM/YYYY",
                key="dt_final_2g"
            )
    
    if ano_selecionado != "Todos":
        df_filtrado = df[df["ano"] == int(ano_selecionado)].copy()
    else:
        df_filtrado = df.copy()
    if orgao_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["orgao"] == orgao_selecionado]
    if classe_selecionada != "Todos":
        df_filtrado = df_filtrado[df_filtrado["classe"] == classe_selecionada]
    if dt_inicial and dt_final:
        df_filtrado = df_filtrado[
            (df_filtrado["dt_distribuicao"].dt.date >= dt_inicial) &
            (df_filtrado["dt_distribuicao"].dt.date <= dt_final)
        ]
    st.caption(
        f"**Total carregado:** {len(df):,} processos".replace(",", ".")
    )
    st.caption(
        f"**Após filtros:** {len(df_filtrado):,} processos".replace(",", ".")
    )
    st.caption("ℹ️ Processos de Corregedoria excluídos")
    # ========== KPIs ==========
    st.markdown("### 📊 Indicadores")
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    total = len(df_filtrado)
    arquivados = (df_filtrado["situacao"] == "Arquivado").sum()
    expedidos = (df_filtrado["situacao"] == "Expedido/Devolvido").sum()
    em_trami = (df_filtrado["situacao"] == "Em tramitação").sum()
    
    # Cálculo do IAD (Índice de Atendimento à Demanda)
    processos_baixados = arquivados + expedidos
    iad = (processos_baixados / total * 100) if total > 0 else 0
    
    # Cálculo do Tempo Médio de Tramitação
    data_atual = datetime.now().date()
    
    def calcular_dias_tramitacao(dt):
        if pd.isna(dt):
            return 0
        return (data_atual - dt.date()).days
    
    # Tempo médio para processos em tramitação
    df_em_tramitacao = df_filtrado[df_filtrado["situacao"] == "Em tramitação"].copy()
    if not df_em_tramitacao.empty:
        df_em_tramitacao["dias_tramitacao"] = df_em_tramitacao["dt_distribuicao"].apply(calcular_dias_tramitacao)
        tempo_medio_tramitacao = df_em_tramitacao["dias_tramitacao"].mean()
    else:
        tempo_medio_tramitacao = 0
    
    # Tempo médio geral (todos os processos)
    df_filtrado_copy = df_filtrado.copy()
    df_filtrado_copy["dias_tramitacao_geral"] = df_filtrado_copy["dt_distribuicao"].apply(calcular_dias_tramitacao)
    tempo_medio_geral = df_filtrado_copy["dias_tramitacao_geral"].mean() if not df_filtrado_copy.empty else 0
    
    col1.metric("Total", f"{total:,}".replace(",", "."))
    col2.metric("Arquivados", f"{arquivados:,}".replace(",", "."),
                f"{arquivados/total*100:.1f}%" if total else "0%")
    col3.metric("Expedidos/Devolvidos", f"{expedidos:,}".replace(",", "."),
                f"{expedidos/total*100:.1f}%" if total else "0%")
    col4.metric("Em tramitação", f"{em_trami:,}".replace(",", "."),
                f"{em_trami/total*100:.1f}%" if total else "0%")
    col5.metric("IAD", f"{iad:.1f}%",
                f"{processos_baixados:,} baixados".replace(",", "."))
    col6.metric("Tempo Médio Tramitação", f"{tempo_medio_tramitacao:.0f} dias",
                f"{em_trami:,} processos".replace(",", "."))
    col7.metric("Tempo Médio Geral", f"{tempo_medio_geral:.0f} dias",
                f"{total:,} processos".replace(",", "."))
    st.markdown("---")
    # ========== GRÁFICOS ==========
    # Gráfico 1: Distribuição temporal (ano ou mês)
    col_esq, col_dir = st.columns(2)
    with col_esq:
        if ano_selecionado == "Todos":
            st.markdown("#### Processos por Ano")
            por_ano = df_filtrado.groupby("ano").size().reset_index(name="qtd")
            fig = px.bar(
                por_ano, x="ano", y="qtd",
                labels={"ano": "Ano", "qtd": "Quantidade"},
                color_discrete_sequence=["#3b82f6"],
            )
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(f"#### Processos por Mês — {ano_selecionado}")
            por_mes = df_filtrado.groupby("mes").size().reset_index(name="qtd")
            nomes_meses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
            por_mes["mes_nome"] = por_mes["mes"].apply(lambda m: nomes_meses[int(m)-1])
            fig = px.bar(
                por_mes, x="mes_nome", y="qtd",
                labels={"mes_nome": "Mês", "qtd": "Quantidade"},
                color_discrete_sequence=["#3b82f6"],
            )
            fig.update_layout(showlegend=False, height=350,
                              xaxis={"categoryorder":"array", "categoryarray": nomes_meses})
            st.plotly_chart(fig, use_container_width=True)
    with col_dir:
        st.markdown("#### Top 10 Classes Processuais")
        top_classes = df_filtrado["classe"].value_counts().head(10).reset_index()
        top_classes.columns = ["classe", "qtd"]
        fig = px.bar(
            top_classes, x="qtd", y="classe", orientation="h",
            labels={"classe": "", "qtd": "Quantidade"},
            color_discrete_sequence=["#6366f1"],
        )
        fig.update_layout(showlegend=False, height=350,
                          yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(fig, use_container_width=True)
    # Segunda linha de gráficos
    col_esq, col_dir = st.columns(2)
    with col_esq:
        st.markdown("#### Situação Atual")
        sit_counts = df_filtrado["situacao"].value_counts().reset_index()
        sit_counts.columns = ["situacao", "qtd"]
        fig = px.pie(
            sit_counts, values="qtd", names="situacao", hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    with col_dir:
        st.markdown("#### Tipo de Decisão")
        dec_counts = df_filtrado["decisao"].value_counts().reset_index()
        dec_counts.columns = ["decisao", "qtd"]
        fig = px.pie(
            dec_counts, values="qtd", names="decisao", hole=0.4,
            color_discrete_sequence=["#3b82f6", "#f59e0b", "#6b7280"],
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    # Terceira linha: Unidades organizacionais
    st.markdown("#### Distribuição por Unidade (CPROC / ASSESSORIA / OUTRAS)")
    col_esq, col_dir = st.columns([1, 2])
    with col_esq:
        unid_counts = df_filtrado["unidade"].value_counts().reset_index()
        unid_counts.columns = ["unidade", "qtd"]
        fig = px.pie(
            unid_counts, values="qtd", names="unidade", hole=0.4,
            color_discrete_map={
                "CPROC": "#06b6d4",
                "ASSESSORIA": "#8b5cf6",
                "OUTRAS": "#f59e0b",
                "SEM TAREFA": "#374151",
                "SEM CLASSIFICAÇÃO": "#9ca3af",
            },
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    with col_dir:
        unid_ano = df_filtrado.groupby(["ano", "unidade"]).size().reset_index(name="qtd")
        fig = px.bar(
            unid_ano, x="ano", y="qtd", color="unidade",
            labels={"ano": "Ano", "qtd": "Quantidade", "unidade": "Unidade"},
            color_discrete_map={
                "CPROC": "#06b6d4",
                "ASSESSORIA": "#8b5cf6",
                "OUTRAS": "#f59e0b",
                "SEM TAREFA": "#374151",
                "SEM CLASSIFICAÇÃO": "#9ca3af",
            },
        )
        fig.update_layout(height=300, barmode="stack")
        st.plotly_chart(fig, use_container_width=True)
    # ========== TABELA DE ÓRGÃOS JULGADORES ==========
    st.markdown("---")
    st.markdown("#### Top 15 Órgãos Julgadores")
    top_orgaos = df_filtrado["orgao"].value_counts().head(15).reset_index()
    top_orgaos.columns = ["Órgão Julgador", "Quantidade"]
    top_orgaos.index = top_orgaos.index + 1
    st.dataframe(top_orgaos, use_container_width=True, height=400)
    
    # ========== RANKING IAD POR ÓRGÃO JULGADOR ==========
    st.markdown("---")
    st.markdown("#### 📊 Ranking IAD por Órgão Julgador")
    
    # Calcular IAD por órgão
    iad_por_orgao = []
    for orgao in df_filtrado["orgao"].unique():
        df_orgao = df_filtrado[df_filtrado["orgao"] == orgao]
        total_orgao = len(df_orgao)
        if total_orgao > 0:
            baixados_orgao = ((df_orgao["situacao"] == "Arquivado") | (df_orgao["situacao"] == "Expedido/Devolvido")).sum()
            iad_orgao = (baixados_orgao / total_orgao) * 100
            iad_por_orgao.append({
                "Órgão Julgador": orgao,
                "Total Processos": total_orgao,
                "Processos Baixados": baixados_orgao,
                "IAD (%)": round(iad_orgao, 1)
            })
    
    # Ordenar por IAD decrescente
    iad_por_orgao.sort(key=lambda x: x["IAD (%)"], reverse=True)
    
    # Criar DataFrame e exibir
    df_iad_ranking = pd.DataFrame(iad_por_orgao)
    df_iad_ranking.index = df_iad_ranking.index + 1
    
    # Formatar colunas
    df_iad_ranking["Total Processos"] = df_iad_ranking["Total Processos"].apply(lambda x: f"{x:,}".replace(",", "."))
    df_iad_ranking["Processos Baixados"] = df_iad_ranking["Processos Baixados"].apply(lambda x: f"{x:,}".replace(",", "."))
    df_iad_ranking["IAD (%)"] = df_iad_ranking["IAD (%)"].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(df_iad_ranking, use_container_width=True, height=400)
    
    # ========== RANKING TEMPO MÉDIO DE TRAMITAÇÃO POR ÓRGÃO JULGADOR ==========
    st.markdown("---")
    st.markdown("#### ⏱️ Ranking Tempo Médio de Tramitação por Órgão Julgador")
    
    # Calcular tempo médio de tramitação por órgão
    tempo_por_orgao = []
    data_atual = datetime.now().date()
    
    def calcular_dias_tramitacao(dt):
        if pd.isna(dt):
            return 0
        return (data_atual - dt.date()).days
    
    for orgao in df_filtrado["orgao"].unique():
        df_orgao = df_filtrado[df_filtrado["orgao"] == orgao].copy()
        total_orgao = len(df_orgao)
        
        if total_orgao > 0:
            # Calcular dias de tramitação para todos os processos do órgão
            df_orgao_copy = df_orgao.copy()
            df_orgao_copy["dias_tramitacao"] = df_orgao_copy["dt_distribuicao"].apply(calcular_dias_tramitacao)
            tempo_medio_orgao = df_orgao_copy["dias_tramitacao"].mean()
            
            # Contar processos em tramitação
            em_tramitacao_orgao = (df_orgao["situacao"] == "Em tramitação").sum()
            
            tempo_por_orgao.append({
                "Órgão Julgador": orgao,
                "Total Processos": total_orgao,
                "Em Tramitação": em_tramitacao_orgao,
                "Tempo Médio (dias)": round(tempo_medio_orgao, 1)
            })
    
    # Ordenar por tempo médio crescente (menor para maior)
    tempo_por_orgao.sort(key=lambda x: x["Tempo Médio (dias)"])
    
    # Criar DataFrame e exibir
    df_tempo_ranking = pd.DataFrame(tempo_por_orgao)
    df_tempo_ranking.index = df_tempo_ranking.index + 1
    
    # Formatar colunas
    df_tempo_ranking["Total Processos"] = df_tempo_ranking["Total Processos"].apply(lambda x: f"{x:,}".replace(",", "."))
    df_tempo_ranking["Em Tramitação"] = df_tempo_ranking["Em Tramitação"].apply(lambda x: f"{x:,}".replace(",", "."))
    df_tempo_ranking["Tempo Médio (dias)"] = df_tempo_ranking["Tempo Médio (dias)"].apply(lambda x: f"{x:.1f}")
    
    st.dataframe(df_tempo_ranking, use_container_width=True, height=400)

# ========== RODAPÉ ==========
st.markdown("---")
st.caption(
    "Dashboard PJe · Tribunal Regional Eleitoral do Ceará · "
    "Dados atualizados conforme CSVs carregados na pasta `data/`"
)
