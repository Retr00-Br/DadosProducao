import streamlit as st
import os

st.set_page_config(page_title="Master Higimed — BI", page_icon="🏥", layout="wide")

# Carregar CSS
if os.path.exists("assets/custom.css"):
    with open("assets/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🏥 Master Higimed — BI Operacional")
st.markdown("Selecione uma das opções no menu lateral para visualizar o **Painel Operacional**, **Ranking de Separadores** ou **Conferentes**.")