import pandas as pd
import numpy as np
import datetime
import os
import streamlit as st

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

def processar_e_consolidar_planilhas(file_rambo, file_producao):
    """
    Lê os arquivos enviados via Streamlit, processa e grava os Parquets otimizados.
    """
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # 1. Processar Operação Rambo (Aba SEPARAÇÃO)
    df_sep = pd.read_excel(file_rambo, sheet_name='SEPARAÇÃO')
    
    cols_rename_sep = {
        'NF': 'nr_nf',
        'PV': 'nr_pv',
        'SEPARADOR': 'separador',
        'DATA': 'data',
        "SKU'S": 'qtd_skus',
        'STATUS PRODUÇÃO': 'status_producao',
        'STATUS': 'status_backlog',
        'VOLUMES': 'volumes',
        'PALETES': 'paletes',
        'CLIENTE': 'cliente'
    }
    df_sep = df_sep.rename(columns=cols_rename_sep)
    
    df_sep['data'] = pd.to_datetime(df_sep['data'], errors='coerce').dt.date
    df_sep = df_sep.dropna(subset=['data'])
    
    df_sep['separador'] = df_sep['separador'].astype(str).str.strip().str.upper()
    df_sep['status_producao'] = df_sep['status_producao'].astype(str).str.strip().str.upper()
    df_sep['status_backlog'] = df_sep['status_backlog'].astype(str).str.strip().str.upper()
    
    df_sep['qtd_skus'] = pd.to_numeric(df_sep['qtd_skus'], errors='coerce').fillna(0)
    df_sep['volumes'] = pd.to_numeric(df_sep['volumes'], errors='coerce').fillna(0)
    df_sep['paletes'] = pd.to_numeric(df_sep['paletes'], errors='coerce').fillna(0)
    
    # Flag para Backlog Realizado (Quando era Backlog e foi Faturado)
    df_sep['is_backlog'] = df_sep['status_backlog'].apply(lambda x: 1 if 'BACKLOG' in x else 0)
    df_sep['is_faturado'] = df_sep['status_producao'].apply(lambda x: 1 if 'FATURADO' in x else 0)
    df_sep['backlog_realizado'] = np.where((df_sep['is_backlog'] == 1) & (df_sep['is_faturado'] == 1), 1, 0)

    # 2. Processar DadosProducao (Aba Resumo Operacao)
    df_prod = pd.read_excel(file_producao, sheet_name='Resumo Operacao')
    df_prod = df_prod[~df_prod['Dias'].astype(str).str.contains('Média|Soma|Total', case=False, na=False)].copy()
    
    cols_rename_prod = {
        'Dias': 'data',
        'Contagem de Nr.NF': 'nfs_emitidas',
        'Pedido Diarios': 'pedidos_diarios',
        'Pendente de Produção': 'pendente_producao'
    }
    df_prod = df_prod.rename(columns=cols_rename_prod)
    df_prod['data'] = pd.to_datetime(df_prod['data'], errors='coerce').dt.date
    df_prod = df_prod.dropna(subset=['data'])
    
    for col in ['nfs_emitidas', 'pedidos_diarios', 'pendente_producao']:
        df_prod[col] = pd.to_numeric(df_prod[col], errors='coerce').fillna(0)

    # Salvar em Parquet
    file_sep_parquet = os.path.join(PROCESSED_DIR, "separacao.parquet")
    file_prod_parquet = os.path.join(PROCESSED_DIR, "producao.parquet")
    
    df_sep.to_parquet(file_sep_parquet, index=False)
    df_prod.to_parquet(file_prod_parquet, index=False)
    
    return file_sep_parquet, file_prod_parquet


@st.cache_data
def carregar_dados_parquet():
    """
    Lê os ficheiros Parquet gerados para o BI com altíssima performance.
    """
    file_sep_parquet = os.path.join(PROCESSED_DIR, "separacao.parquet")
    file_prod_parquet = os.path.join(PROCESSED_DIR, "producao.parquet")
    
    if not os.path.exists(file_sep_parquet) or not os.path.exists(file_prod_parquet):
        return None, None
        
    df_sep = pd.read_parquet(file_sep_parquet)
    df_prod = pd.read_parquet(file_prod_parquet)
    
    return df_sep, df_prod