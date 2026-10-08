import streamlit as st
import pandas as pd
import os
from modules.data_loader import carregar_dados_parquet
from modules.metrics import obter_kpis_gerais
from modules.charts import criar_grafico_nfs_meta, criar_grafico_volume_pecas, criar_grafico_backlogs_realizados
from modules.ml_forecasting import calcular_previsao_demanda

st.set_page_config(page_title="Painel Operacional", page_icon="📊", layout="wide")

if os.path.exists("assets/custom.css"):
    with open("assets/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

df_sep, df_prod = carregar_dados_parquet()

if df_prod is None:
    st.warning("⚠️ Nenhuma base de dados encontrada. Por favor, acesse o `admin_app.py` para realizar a ingestão das planilhas.")
    st.stop()

# Filtro de Período
st.sidebar.header("📅 Período")
min_d, max_d = df_prod['data'].min(), df_prod['data'].max()
periodo = st.sidebar.date_input("Intervalo:", value=(min_d, max_d), min_value=min_d, max_value=max_d)

if isinstance(periodo, tuple) and len(periodo) == 2:
    d1, d2 = periodo
    df_prod_f = df_prod[(df_prod['data'] >= d1) & (df_prod['data'] <= d2)]
    df_sep_f = df_sep[(df_sep['data'] >= d1) & (df_sep['data'] <= d2)]
else:
    df_prod_f, df_sep_f = df_prod.copy(), df_sep.copy()

# KPIs
total_nfs, media_nfs, total_skus, media_backlog = obter_kpis_gerais(df_prod_f, df_sep_f)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total NFs</div><div class="kpi-value">{total_nfs:,}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Média NFs / Dia</div><div class="kpi-value">{media_nfs:.1f}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Peças (SKU)</div><div class="kpi-value">{total_skus:,}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Média Backlog / Dia</div><div class="kpi-value">{media_backlog:.1f}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_g1, col_g2 = st.columns(2)
with col_g1:
    st.markdown("##### 🎯 NFs Emitidas vs. Meta Diária (120)")
    st.plotly_chart(criar_grafico_nfs_meta(df_prod_f), use_container_width=True)

with col_g2:
    st.markdown("##### 📦 Volume Total de Peças Processadas por Dia")
    st.plotly_chart(criar_grafico_volume_pecas(df_sep_f), use_container_width=True)

st.markdown("##### ⏳ Backlogs Realizados por Dia (Status Faturado)")
st.plotly_chart(criar_grafico_backlogs_realizados(df_sep_f), use_container_width=True)

# Módulo de ML (Previsão)
with st.expander("🤖 Previsão de Demanda (Machine Learning)"):
    df_forecast = calcular_previsao_demanda(df_prod_f)
    if not df_forecast.empty:
        st.dataframe(df_forecast, use_container_width=True)