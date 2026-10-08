import streamlit as st
import os

st.set_page_config(page_title="Ranking Conferentes", page_icon="🔍", layout="wide")

if os.path.exists("assets/custom.css"):
    with open("assets/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🔍 Desempenho & Ranking de Conferentes")
st.info("💡 Módulo em estruturação. Assim que o campo com os nomes dos conferentes for mapeado na base, os gráficos de produtividade serão disponibilizados nesta aba.")