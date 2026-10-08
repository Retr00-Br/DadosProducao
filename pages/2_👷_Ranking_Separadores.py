import streamlit as st
import os
from modules.data_loader import carregar_dados_parquet
from modules.charts import criar_grafico_ranking_separadores_nfs, criar_grafico_ranking_separadores_skus

st.set_page_config(page_title="Ranking Separadores", page_icon="👷", layout="wide")

if os.path.exists("assets/custom.css"):
    with open("assets/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

df_sep, _ = carregar_dados_parquet()

if df_sep is None:
    st.warning("⚠️ Nenhuma base de dados encontrada.")
    st.stop()

st.title("👷 Desempenho & Ranking de Separadores")

c1, c2 = st.columns(2)
with c1:
    st.markdown("##### 🏆 Top Separadores por NFs Distintas")
    st.plotly_chart(criar_grafico_ranking_separadores_nfs(df_sep), use_container_width=True)

with c2:
    st.markdown("##### 📦 Top Separadores por Peças / SKUs Movimentados")
    st.plotly_chart(criar_grafico_ranking_separadores_skus(df_sep), use_container_width=True)