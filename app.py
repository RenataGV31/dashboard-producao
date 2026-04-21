import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# CONFIGURAÇÃO DA PÁGINA
# ==============================
st.set_page_config(
    page_title="Dashboard Gerencial de Produção",
    layout="wide",
    page_icon="💠"
)

# ==============================
# ESTILO – DESIGN AMIGOZ
# ==============================
st.markdown("""
<style>
.main {
    background-color: #f4f8fb;
}

.header {
    background: linear-gradient(90deg, #00A3E0, #0077B6);
    padding: 30px;
    border-radius: 12px;
    color: white;
    margin-bottom: 25px;
}

.kpi {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# ==============================
# CABEÇALHO
# ==============================
st.markdown("""
<div class="header">
    <h1>Dashboard Gerencial de Produção</h1>
    <p>Análise semanal por convênio • Estilo AMIGOZ</p>
</div>
""", unsafe_allow_html=True)

# ==============================
# UPLOAD EXCEL
# ==============================
arquivo = st.file_uploader(
    "📂 Envie o arquivo EXCEL",
    type=["xlsx", "xls"]
)

if arquivo:
    # ==============================
    # LEITURA DO EXCEL
    # ==============================
    df = pd.read_excel(arquivo, engine="openpyxl")

    # ==============================
    # TRATAMENTO
    # ==============================
    df["Data Cadastro"] = pd.to_datetime(df["Data Cadastro"])

    df["Valor Proposta"] = (
        df["Valor Proposta"]
        .astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    df["Semana"] = df["Data Cadastro"].dt.to_period("W").astype(str)

    # ==============================
    # AGREGAÇÃO
    # ==============================
    resumo = (
        df.groupby(["Convenio", "Semana"])
        .agg(
            Quantidade=("Nr Proposta", "count"),
            Valor_Total=("Valor Proposta", "sum")
        )
        .reset_index()
        .sort_values(["Semana", "Valor_Total"], ascending=[False, False])
    )

    ultima_semana = resumo["Semana"].max()
    atual = resumo[resumo["Semana"] == ultima_semana]

    # ==============================
    # KPIs
    # ==============================
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("<div class='kpi'>", unsafe_allow_html=True)
        st.metric("💰 Produção Total", f"R$ {df['Valor Proposta'].sum():,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='kpi'>", unsafe_allow_html=True)
        st.metric("📅 Última Semana", f"R$ {atual['Valor_Total'].sum():,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown("<div class='kpi'>", unsafe_allow_html=True)
        st.metric("🏆 Convênio Líder", atual.groupby("Convenio")["Valor_Total"].sum().idxmax())
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ==============================
    # RANKING
    # ==============================
    ranking = (
        atual.groupby("Convenio")["Valor_Total"]
        .sum()
        .sort_values(ascending=True)
        .reset_index()
    )

    fig_rank = px.bar(
        ranking,
        x="Valor_Total",
        y="Convenio",
        orientation="h",
        color="Valor_Total",
        color_continuous_scale="Blues",
        title="🏆 Ranking de Convênios – Maior Produção (Semana Atual)"
    )

    st.plotly_chart(fig_rank, use_container_width=True)

    # ==============================
    # TABELA
    # ==============================
    st.subheader("📋 Detalhamento da Produção")
    st.dataframe(resumo, use_container_width=True)
