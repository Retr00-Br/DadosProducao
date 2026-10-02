import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E PALETA HIGIMED
# ==========================================
st.set_page_config(
    page_title="HIGIMED — Operação & Produção",
    page_icon="🏥",
    layout="wide"
)

# Paleta de Cores HIGIMED / Master
COLOR_PRIMARY = "#0088CC"     # Cyan/Azul HIGIMED Principal
COLOR_SECONDARY = "#0A2B4C"   # Azul Marinho Executivo
COLOR_ACCENT = "#4FA8DE"      # Azul Claro de Suporte
COLOR_BG_CARD = "#F4F8FA"     # Fundo dos Cards de KPI
COLOR_ALERT = "#E63946"       # Cor de Alerta para Pendências Altas
COLOR_SUCCESS = "#10B981"     # Verde para Metas Alcançadas

# Estilização CSS dos Cards e Interface estilo BI
st.markdown(f"""
    <style>
        [data-testid="stSidebar"] {{
            background-color: #F8FAFC;
        }}
        .main-title {{
            color: {COLOR_SECONDARY};
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 2px;
        }}
        .sub-title {{
            color: #64748B;
            font-size: 1rem;
            margin-bottom: 20px;
        }}
        .kpi-card {{
            background-color: {COLOR_BG_CARD};
            border-left: 5px solid {COLOR_PRIMARY};
            border-radius: 8px;
            padding: 16px 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        }}
        .kpi-title {{
            color: #64748B;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .kpi-value {{
            color: {COLOR_SECONDARY};
            font-size: 1.8rem;
            font-weight: 800;
            margin-top: 4px;
        }}
    </style>
""", unsafe_allow_html=True)

def aplicar_estilo_higimed():
    sns.set_theme(style="whitegrid", font="sans-serif")
    plt.rcParams.update({
        'figure.facecolor': 'none',
        'axes.facecolor': 'none',
        'axes.edgecolor': '#E2E8F0',
        'axes.labelcolor': COLOR_SECONDARY,
        'axes.titlesize': 12,
        'axes.titleweight': 'bold',
        'axes.titlecolor': COLOR_SECONDARY,
        'xtick.color': '#64748B',
        'ytick.color': '#64748B',
        'font.size': 9
    })

aplicar_estilo_higimed()

# ==========================================
# 2. HEADER DA APLICAÇÃO COM LOGO
# ==========================================
col_logo, col_titulo = st.columns([1, 4])

with col_logo:
    # Tenta carregar a imagem 'logo.png' da pasta local
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    elif os.path.exists("logo2.png"):
        st.image("logo2.png", use_container_width=True)
    else:
        st.write("🏥") # Fallback visual caso não encontre o arquivo de imagem

with col_titulo:
    st.markdown("<div class='main-title'>HIGIMED — Painel de Produção & Operação</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Acompanhamento diário de NFs, metas, pendências e volumes de SKU</div>", unsafe_allow_html=True)

# ==========================================
# 3. CARREGAMENTO E TRATAMENTO DA PLANILHA
# ==========================================
st.sidebar.header("📁 Importar Planilha")
arquivo = st.sidebar.file_uploader("Envie a planilha em Excel (.xlsx)", type=["xlsx"])

# Opção complementar para upload de logo na barra lateral se desejar trocar
logo_upload = st.sidebar.file_uploader("Alterar Logo (Opcional)", type=["png", "jpg", "jpeg"])
if logo_upload is not None:
    with open("logo.png", "wb") as f:
        f.write(logo_upload.getbuffer())
    st.sidebar.success("Logo atualizada!")

@st.cache_data
def processar_dados(file):
    # Lê a primeira aba da planilha
    df = pd.read_excel(file, sheet_name=0)
    
    # Remover linhas finais de Resumo/Média da planilha
    df = df[~df['Dias'].astype(str).str.contains('Média|Soma|Total', case=False, na=False)].copy()
    
    # Tratamento de tipos numéricos
    df['Contagem de Nr.NF'] = pd.to_numeric(df['Contagem de Nr.NF'], errors='coerce').fillna(0)
    df['Pedido Diarios'] = pd.to_numeric(df['Pedido Diarios'], errors='coerce').fillna(0)
    df['Pendente de Produção'] = pd.to_numeric(df['Pendente de Produção'], errors='coerce').fillna(0)
    df['Contagem de SKU'] = pd.to_numeric(df['Contagem de SKU'], errors='coerce').fillna(0)
    
    # Limpa coluna de Qtd Total SKU (extrai apenas os números)
    df['Soma de Qtd Total SKU'] = df['Soma de Qtd Total SKU'].astype(str).str.extract(r'(\d+)')[0]
    df['Soma de Qtd Total SKU'] = pd.to_numeric(df['Soma de Qtd Total SKU'], errors='coerce').fillna(0)
    
    return df

if arquivo is not None:
    df = processar_dados(arquivo)
    st.sidebar.success("Planilha carregada com sucesso!")
else:
    st.info("💡 **Por favor, envie o arquivo Excel na barra lateral** para carregar os gráficos do painel.")
    st.stop()

# ==========================================
# 4. FILTROS INTERATIVOS
# ==========================================
st.sidebar.header("🔍 Filtro de Período")
dias_disponiveis = df['Dias'].tolist()
dias_selecionados = st.sidebar.multiselect(
    "Filtrar por Dias:",
    options=dias_disponiveis,
    default=dias_disponiveis
)

df_filtrado = df[df['Dias'].isin(dias_selecionados)]

if df_filtrado.empty:
    st.warning("Selecione pelo menos um dia no filtro para visualizar os dados.")
    st.stop()

# ==========================================
# 5. CARDS DE KPI (RESUMO EXECUTIVO)
# ==========================================
total_nf = df_filtrado['Contagem de Nr.NF'].sum()
media_nf_dia = df_filtrado['Contagem de Nr.NF'].mean()
total_qtd_sku = df_filtrado['Soma de Qtd Total SKU'].sum()
media_pendentes = df_filtrado['Pendente de Produção'].mean()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total NFs Emitidas</div>
            <div class="kpi-value">{int(total_nf):,}</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Média de NFs / Dia</div>
            <div class="kpi-value">{media_nf_dia:.1f}</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Peças Processadas (SKU)</div>
            <div class="kpi-value">{int(total_qtd_sku):,}</div>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: {COLOR_SUCCESS if media_pendentes <= 20 else COLOR_ALERT};">
            <div class="kpi-title">Média Pendente / Dia</div>
            <div class="kpi-value">{media_pendentes:.1f}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 6. GRÁFICOS PAINEL BI (MATPLOTLIB / SEABORN)
# ==========================================

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.markdown("##### 🎯 NFs Emitidas vs. Meta Diária (120)")
    fig1, ax1 = plt.subplots(figsize=(7, 4))
    
    sns.barplot(data=df_filtrado, x='Dias', y='Contagem de Nr.NF', color=COLOR_PRIMARY, ax=ax1)
    ax1.axhline(y=120, color=COLOR_SECONDARY, linestyle='--', linewidth=1.8, label='Meta Diária (120)')
    
    ax1.set_xlabel("")
    ax1.set_ylabel("Contagem de NFs")
    plt.xticks(rotation=90, fontsize=8)
    sns.despine(top=True, right=True)
    ax1.legend(loc="upper right", frameon=False)
    
    st.pyplot(fig1)

with col_graf2:
    st.markdown("##### 📦 Volume Total de Peças Processadas por Dia")
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    
    sns.lineplot(data=df_filtrado, x='Dias', y='Soma de Qtd Total SKU', color=COLOR_SECONDARY, marker='o', linewidth=2, ax=ax2)
    ax2.fill_between(range(len(df_filtrado)), df_filtrado['Soma de Qtd Total SKU'], color=COLOR_PRIMARY, alpha=0.15)
    
    ax2.set_xlabel("")
    ax2.set_ylabel("Quantidade Total SKU")
    plt.xticks(rotation=90, fontsize=8)
    sns.despine(top=True, right=True)
    
    st.pyplot(fig2)

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    st.markdown("##### ⏳ Saldo de Pendência de Produção Diária")
    fig3, ax3 = plt.subplots(figsize=(7, 4))
    
    cores_pendencia = [COLOR_ALERT if x > 0 else COLOR_SUCCESS for x in df_filtrado['Pendente de Produção']]
    
    sns.barplot(data=df_filtrado, x='Dias', y='Pendente de Produção', palette=cores_pendencia, ax=ax3)
    ax3.axhline(y=0, color='gray', linewidth=0.8)
    
    ax3.set_xlabel("")
    ax3.set_ylabel("Pendência (Pedidos)")
    plt.xticks(rotation=90, fontsize=8)
    sns.despine(top=True, right=True)
    
    st.pyplot(fig3)

with col_graf4:
    st.markdown("##### 🏷️ Diversidade de SKUs Únicos Movimentados por Dia")
    fig4, ax4 = plt.subplots(figsize=(7, 4))
    
    sns.barplot(data=df_filtrado, x='Dias', y='Contagem de SKU', color=COLOR_ACCENT, ax=ax4)
    
    ax4.set_xlabel("")
    ax4.set_ylabel("Variedade de SKUs")
    plt.xticks(rotation=90, fontsize=8)
    sns.despine(top=True, right=True)
    
    st.pyplot(fig4)

# Exibição da Tabela Trada
with st.expander("📄 Visualizar Tabela Tratada da Operação"):
    st.dataframe(df_filtrado, use_container_width=True)
