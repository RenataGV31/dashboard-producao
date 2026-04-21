import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# CONFIGURAÇÃO DA PÁGINA
# ==============================
st.set_page_config(
    page_title="Dashboard Gerencial - Produção",
    layout="wide",
    page_icon="📊"
)

# ==============================
# ESTILO (AZUL CLARO – GERENCIAL)
# ==============================
st.markdown(
    """
    <style>
        .stMetric {
            background-color: #EAF2FB;
            padding: 15px;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# TÍTULO
# ==============================
st.title("📊 Dashboard Gerencial de Produção")
st.caption("Análise semanal por convênio com ranking e KPIs")

# ==============================
# UPLOAD DO CSV
# ==============================
arquivo = st.file_uploader("📂 Envie o arquivo CSV", type=["csv"])

if arquivo is not None:
    # ==============================
    # LEITURA E TRATAMENTO DOS DADOS
    # ==============================
    df = pd.read_csv(arquivo)

    df["Data Cadastro"] = pd.to_datetime(df["Data Cadastro"])
    df["Semana"] = df["Data Cadastro"].dt.strftime("%Y-%U")

    df["Valor Proposta"] = (
        df["Valor Proposta"]
        .str.replace("R$", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    # ==============================
    # AGREGAÇÃO SEMANAL POR CONVÊNIO
    # ==============================
    resumo = (
        df.groupby(["Convenio", "Semana"])
        .agg(
            Quantidade=("Nr Proposta", "count"),
            Valor_Total=("Valor Proposta", "sum")
        )
        .reset_index()
        .sort_values(["Convenio", "Semana"])
    )

    resumo["Variação %"] = resumo.groupby("Convenio")["Valor_Total"].pct_change() * 100

    resumo["Tendência"] = resumo["Variação %"].apply(
        lambda x: "🔼 Aumentou" if x > 0 else "🔽 Caiu" if x < 0 else "➖ Estável"
    )

    # ==============================
    # DEFINIÇÃO DAS SEMANAS
    # ==============================
    semanas = resumo["Semana"].unique()

    if len(semanas) >= 2:
        ultima_semana = semanas[-1]
        semana_anterior = semanas[-2]
    else:
        ultima_semana = semanas[-1]
        semana_anterior = semanas[-1]

    atual = resumo[resumo["Semana"] == ultima_semana]
    anterior = resumo[resumo["Semana"] == semana_anterior]

    producao_atual = atual["Valor_Total"].sum()
    producao_anterior = anterior["Valor_Total"].sum()

    variacao_geral = (
        (producao_atual / producao_anterior - 1) * 100
        if producao_anterior > 0 else 0
    )

    top_convenio = (
        atual.groupby("Convenio")["Valor_Total"]
        .sum()
        .sort_values(ascending=False)
        .idxmax()
    )

    # ==============================
    # KPIs
    # ==============================
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric(
        "Produção Total",
        f"R$ {df['Valor Proposta'].sum():,.2f}"
    )

    kpi2.metric(
        "Produção Última Semana",
        f"R$ {producao_atual:,.2f}"
    )

    kpi3.metric(
        "Variação Semana (%)",
        f"{variacao_geral:.2f}%",
        delta=f"{variacao_geral:.2f}%"
    )

    kpi4.metric(
        "Convênio Destaque",
        top_convenio
    )

    st.divider()

    # ==============================
    # RANKING DE CONVÊNIOS
    # ==============================
    st.subheader("🏆 Ranking de Convênios – Maior Produção (Última Semana)")

    ranking = (
        atual.groupby("Convenio")["Valor_Total"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig_rank = px.bar(
        ranking,
        x="Valor_Total",
        y="Convenio",
        orientation="h",
        color="Valor_Total",
        color_continuous_scale="Blues",
        labels={"Valor_Total": "Valor Produzido (R$)", "Convenio": "Convênio"}
    )

    st.plotly_chart(fig_rank, use_container_width=True)

    # ==============================
    # EVOLUÇÃO SEMANAL
    # ==============================
    st.subheader("📈 Evolução Semanal por Convênio")

    fig_line = px.line(
        resumo,
        x="Semana",
        y="Valor_Total",
        color="Convenio",
        markers=True,
        labels={
            "Valor_Total": "Valor Produzido (R$)",
            "Semana": "Semana"
        }
    )

    st.plotly_chart(fig_line, use_container_width=True)

    # ==============================
    # TABELA ANALÍTICA
    # ==============================
    st.subheader("📋 Visão Analítica Detalhada")

    st.dataframe(
        resumo.sort_values(["Semana", "Valor_Total"], ascending=[False, False]),
        use_container_width=True
    )
