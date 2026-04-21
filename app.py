import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- CONFIGURAÇÃO DA PÁGINA ----------
st.set_page_config("page_title=""Dashboard Gerencial - Produção",
"layout=""wide",
"page_icon=""📊"")

# ---------- ESTILO (AZUL CLARO) ----------
st.markdown(""""
<style>
    .stMetric {
        background-color: #EAF2FB;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""",
"unsafe_allow_html=True)

st.title(""📊 Dashboard Gerencial de Produção"")
st.caption(""Análise semanal com ranking de convênios"")

# ---------- UPLOAD ----------
file = st.file_uploader(""📂 Envie o CSV",
"type=""csv"")

if file":"df = pd.read_csv(file)

    # ---------- TRATAMENTO ----------
    df"[
   "Data Cadastro"
]"= pd.to_datetime(df"[
   "Data Cadastro"
]")
    df"[
   "Semana"
]"= df"[
   "Data Cadastro"
]".dt.strftime(""%Y-%U"")

    df"[
   "Valor Proposta"
]"= (
        df"[
   "Valor Proposta"
]".str.replace(""R$",
"",
"regex=False)
        .str.replace("".",
"",
"regex=False)
        .str.replace("",",
".",
"regex=False)
        .astype(float)
    )

    # ---------- AGREGAÇÃO ----------
    resumo = (
        df.groupby("[
   "Convenio",
   "Semana"
]")
        .agg(
            Qtde=(""Nr Proposta",
"count"")",
"Valor=(""Valor Proposta",
"sum"")
        )
        .reset_index()
    )

    resumo = resumo.sort_values("[
   "Convenio",
   "Semana"
]")
    resumo"[
   "Variação %"
]"= resumo.groupby(""Convenio"")"[
   "Valor"
].pct_change() * 100

    resumo[
   "Tendência"
]"= resumo"[
   "Variação %"
]".apply(
        lambda x":"🔼 Aumentou"if x > 0 else"🔽 Caiu"if x < 0 else"➖ Estável"")

    # ---------- ÚLTIMA SEMANA ----------
    ultima_semana = resumo"[
   "Semana"
]".max()
    semana_anterior = resumo"[
   "Semana"
]".sort_values().unique()"[
   -2
]"atual = resumo"[
   "resumo"[
      "Semana"
   ]"== ultima_semana"
]"anterior = resumo"[
   "resumo"[
      "Semana"
   ]"== semana_anterior"
]"crescimento_geral = (
        atual"[
   "Valor"
]".sum() / anterior"[
   "Valor"
].sum() - 1
    ) * 100

    top_convenio = (
        atual.groupby("Convenio"")"[
   "Valor"
].sum()
        .sort_values(ascending=False)
        .idxmax()
    )

    # ---------- KPIs ----------
    kpi1,
kpi2,
kpi3,
kpi4 = st.columns(4)

    kpi1.metric("Produção Total",
"f""R$ {df['Valor Proposta'].sum():,.2f}")
    kpi2.metric("Produção Última Semana",
"f""R$ {atual['Valor'].sum():,.2f}")
    kpi3.metric("Variação Geral %",
"f""{crescimento_geral:.2f}%",
"delta=f""{crescimento_geral:.2f}%")
    kpi4.metric("Convênio Destaque",
"top_convenio)

    st.divider()

    # ---------- RANKING ----------
    st.subheader(""🏆 Ranking de Convênios – Maior Produção (Última Semana)"")

    ranking = (
        atual.groupby(""Convenio"")"[
   "Valor"
]".sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig_rank = px.bar(
        ranking",
"x=""Valor",
"y=""Convenio",
"orientation=""h",
"color=""Valor",
"color_continuous_scale=""Blues",
"title=""Ranking de Convênios por Produção"")
    st.plotly_chart(fig_rank",
"use_container_width=True)

    # ---------- EVOLUÇÃO SEMANAL ----------
    st.subheader(""📈 Evolução Semanal por Convênio"")

    fig_line = px.line(
        resumo",
"x=""Semana",
"y=""Valor",
"color=""Convenio",
"markers=True
    )
    st.plotly_chart(fig_line",
"use_container_width=True)

    # ---------- TABELA ANALÍTICA ----------
    st.subheader(""📋 Visão Analítica Detalhada"")
    st.dataframe(
        resumo.sort_values("[
   "Semana",
   "Valor"
],
"ascending="[
   false,
   false
]")",
"use_container_width=True
    )"