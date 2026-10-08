import streamlit as st
import os
from modules.data_loader import processar_e_consolidar_planilhas

st.set_page_config(page_title="Master Higimed — Portal Ingestão", page_icon="⚙️", layout="centered")

st.title("⚙️ Portal de Ingestão de Dados")
st.caption("Faça o upload das planilhas para atualizar a base Parquet do BI em tempo real.")

file_rambo = st.file_uploader("Planilha: Operação Rambo (.xlsx)", type=["xlsx"])
file_producao = st.file_uploader("Planilha: DadosProducao (.xlsx)", type=["xlsx"])

if st.button("🚀 Processar e Atualizar BI Master"):
    if file_rambo is not None and file_producao is not None:
        with st.spinner("Processando planilhas e gerando base Parquet otimizada..."):
            p1, p2 = processar_e_consolidar_planilhas(file_rambo, file_producao)
            st.success("✅ Base de dados do BI atualizada com sucesso em formato Parquet!")
            st.info(f"Arquivos otimizados gravados em:\n- {p1}\n- {p2}")
    else:
        st.error("Por favor, envie ambos os arquivos .xlsx para continuar.")