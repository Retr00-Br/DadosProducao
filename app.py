import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import os

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E PALETA DARK NAVY
# ==========================================
st.set_page_config(
    page_title="HIGIMED — Operação & Produção",
    page_icon="🏥",
    layout="wide"
)

# Paleta de Cores HIGIMED - Tema Azul Escuro Executivo (Dark Navy)
BG_MAIN = "#0B132B"         # Fundo Geral Azul Bem Escuro
BG_CARD = "#1C2541"         # Fundo dos Cards e Gráficos (Azul Marinho)
COLOR_PRIMARY = "#00B4D8"   # Azul Cyan Brilhante (Destaque Principal)
COLOR_SECONDARY = "#90E0EF" # Azul Claro Suave (Texto e Linhas)
TEXT_WHITE = "#F8FAFC"      # Texto Principal
TEXT_MUTED = "#94A3B8"      # Texto Secundário
COLOR_ALERT = "#FF4D6D"      # Alerta Vermelho Neon
COLOR_SUCCESS = "#38B000"    # Verde Sucesso

# Estilização CSS Personalizada (Tema Escuro BI)
st.markdown(f"""
    <style>
        /* Fundo da Aplicação */
        .stApp {{
            background-color: {BG_MAIN};
            color: {TEXT_WHITE};
        }}
        [data-testid="stSidebar"] {{
            background-color: #0A1128;
        }}
        /* Títulos */
        .main-title {{
            color: {TEXT_WHITE};
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 2px;
        }}
        .sub-title {{
            color: {TEXT_MUTED};
            font-size: 1rem;
            margin-bottom: 20px;
        }}
        /* Cards KPI */
        .kpi-card {{
            background-color: {BG_CARD};
            border-left: 5px solid {COLOR_PRIMARY};
            border-radius: 10px;
            padding: 18px 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .kpi-title {{
            color: {TEXT_MUTED};
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .kpi-value {{
            color: {TEXT_WHITE};
            font-size: 1.9rem;
            font-weight: 800;
            margin-top: 4px;
        }}
    </style>
""", unsafe_allow_html=True)

def aplicar_estilo_higimed_dark():
    sns.set_theme(style="dark", font="sans-serif")
    plt.rcParams.update({
        'figure.facecolor': BG_CARD,
        'axes.facecolor': BG_CARD,
        'axes.edgecolor': '#334155',
        'axes.labelcolor': TEXT_MUTED,
        'axes.titlesize': 13,
        'axes.titleweight': 'bold',
        'axes.titlecolor': TEXT_WHITE,
        'grid.color': '#1E293B',
        'grid.linestyle': '--',
        'grid.alpha': 0.6,
        'xtick.color': TEXT_MUTED,
        'ytick.color': TEXT_MUTED,
        'font.size': 10
    })

aplicar_estilo_higimed_dark()

# ==========================================
# 2. HEADER DA APLICAÇÃO
# ==========================================
col_logo, col_titulo = st.columns([1, 4])

with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    elif os.path.exists("logo2.png"):
        st.image("logo2.png", use_container_width=True)
    else:
        st.write("🏥")

with col_titulo:
    st.markdown("<div class='main-title'>HIGIMED — Painel de Produção & Operação</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Acompanhamento diário de NFs, metas, pendências e volumes de SKU</div>", unsafe_allow_html=True)

# ==========================================
# 3. TRATAMENTO INTELIGENTE DE DATAS (PT-BR)
# ==========================================
MONTH_MAP = {'ago': 8, 'set': 9, 'sep': 9, 'out': 10, 'jul': 7, 'jun': 6}
MONTH_MAP_PT = {8: 'Ago', 9: 'Set', 10: 'Out', 7: 'Jul', 6: 'Jun'}

def parse_dia_to_date(val):
    if isinstance(val, (datetime.datetime, pd.Timestamp)):
        return val.date()
    val_str = str(val).strip().lower()
    try:
        parts = val_str.split('/')
        day = int(parts[0])
        month_str = parts[1]
        month = MONTH_MAP.get(month_str, 8)
        return datetime.date(2026, month, day)
    except Exception:
        return None

def formatar_data_pt(d):
    if pd.isnull(d):
        return ""
    mes_pt = MONTH_MAP_PT.get(d.month, d.strftime('%m'))
    return f"{d.strftime('%d')}/{mes_pt}"

@st.cache_data
def processar_dados(file):
    df = pd.read_excel(file, sheet_name=0)
    
    # Remover linhas de totais ou médias
    df = df[~df['Dias'].astype(str).str.contains('Média|Soma|Total', case=False, na=False)].copy()
    
    # Converter para objeto Date
    df['Data_Obj'] = df['Dias'].apply(parse_dia_to_date)
    df = df.dropna(subset=['Data_Obj']).sort_values('Data_Obj')
    
    # Formatação padronizada em Português (Ex: 03/Ago)
    df['Dia_Formatado'] = df['Data_Obj'].apply(formatar_data_pt)
    
    # Tratamento numérico
    df['Contagem de Nr.NF'] = pd.to_numeric(df['Contagem de Nr.NF'], errors='coerce').fillna(0)
    df['Pedido Diarios'] = pd.to_numeric(df['Pedido Diarios'], errors='coerce').fillna(0)
    df['Pendente de Produção'] = pd.to_numeric(df['Pendente de Produção'], errors='coerce').fillna(0)
    df['Contagem de SKU'] = pd.to_numeric(df['Contagem de SKU'], errors='coerce').fillna(0)
    
    df['Soma de Qtd Total SKU'] = df['Soma de Qtd Total SKU'].astype(str).str.extract(r'(\d+)')[0]
    df['Soma de Qtd Total SKU'] = pd.to_numeric(df['Soma de Qtd Total SKU'], errors='coerce').fillna(0)
    
    return df

st.sidebar.header("📁 Importar Planilha")
arquivo = st.sidebar.file_uploader("Envie a planilha em Excel (.xlsx)", type=["xlsx"])

if arquivo is not None:
    df = processar_dados(arquivo)
    st.sidebar.success("Planilha carregada com sucesso!")
else:
    st.info("💡 **Por favor, envie o arquivo Excel na barra lateral** para carregar os gráficos do painel.")
    st.stop()

# ==========================================
# 4. FILTRO DINÂMICO DE DATA (CALENDÁRIO)
# ==========================================
st.sidebar.header("📅 Filtro de Período")

min_data = df['Data_Obj'].min()
max_data = df['Data_Obj'].max()

periodo = st.sidebar.date_input(
    "Selecione o intervalo:",
    value=(min_data, max_data),
    min_value=min_data,
    max_value=max_data,
    format="DD/MM/YYYY"
)

if isinstance(periodo, tuple) and len(periodo) == 2:
    data_inicio, data_fim = periodo
    df_filtrado = df[(df['Data_Obj'] >= data_inicio) & (df['Data_Obj'] <= data_fim)]
elif isinstance(periodo, tuple) and len(periodo) == 1:
    data_inicio = periodo[0]
    df_filtrado = df[df['Data_Obj'] == data_inicio]
else:
    df_filtrado = df.copy()

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para o período selecionado.")
    st.stop()

# ==========================================
# 5. CARDS DE KPI (TEMA ESCURO)
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
# 6. GRÁFICOS DO PAINEL (CONTRASTE DARK)
# ==========================================

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.markdown("##### 🎯 NFs Emitidas vs. Meta Diária (120)")
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    
    sns.barplot(data=df_filtrado, x='Dia_Formatado', y='Contagem de Nr.NF', color=COLOR_PRIMARY, ax=ax1)
    ax1.axhline(y=120, color=COLOR_ALERT, linestyle='--', linewidth=2, label='Meta Diária (120)')
    
    ax1.set_xlabel("")
    ax1.set_ylabel("Contagem de NFs")
    ax1.tick_params(axis='x', rotation=45, labelsize=8)
    sns.despine(top=True, right=True)
    ax1.legend(loc="upper right", facecolor=BG_CARD, edgecolor='none', labelcolor=TEXT_WHITE)
    
    st.pyplot(fig1, use_container_width=True)

with col_graf2:
    st.markdown("##### 📦 Volume Total de Peças Processadas por Dia")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    
    ax2.plot(df_filtrado['Dia_Formatado'], df_filtrado['Soma de Qtd Total SKU'], color=COLOR_SECONDARY, marker='o', linewidth=2.2, markersize=4)
    ax2.fill_between(range(len(df_filtrado)), df_filtrado['Soma de Qtd Total SKU'], color=COLOR_PRIMARY, alpha=0.25)
    
    ax2.set_xlabel("")
    ax2.set_ylabel("Quantidade Total SKU")
    ax2.tick_params(axis='x', rotation=45, labelsize=8)
    sns.despine(top=True, right=True)
    
    st.pyplot(fig2, use_container_width=True)

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    st.markdown("##### ⏳ Saldo de Pendência de Produção Diária")
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    
    cores_pendencia = [COLOR_ALERT if x > 0 else COLOR_SUCCESS for x in df_filtrado['Pendente de Produção']]
    
    sns.barplot(data=df_filtrado, x='Dia_Formatado', y='Pendente de Produção', palette=cores_pendencia, ax=ax3)
    ax3.axhline(y=0, color='#64748B', linewidth=0.8)
    
    ax3.set_xlabel("")
    ax3.set_ylabel("Pendência (Pedidos)")
    ax3.tick_params(axis='x', rotation=45, labelsize=8)
    sns.despine(top=True, right=True)
    
    st.pyplot(fig3, use_container_width=True)

with col_graf4:
    st.markdown("##### 🏷️ Diversidade de SKUs Únicos Movimentados por Dia")
    fig4, ax4 = plt.subplots(figsize=(10, 5))
    
    sns.barplot(data=df_filtrado, x='Dia_Formatado', y='Contagem de SKU', color=COLOR_SECONDARY, ax=ax4)
    
    ax4.set_xlabel("")
    ax4.set_ylabel("Variedade de SKUs")
    ax4.tick_params(axis='x', rotation=45, labelsize=8)
    sns.despine(top=True, right=True)
    
    st.pyplot(fig4, use_container_width=True)

# Exibição da Tabela Tratada
with st.expander("📄 Visualizar Tabela Tratada da Operação"):
    st.dataframe(
        df_filtrado[['Data_Obj', 'Dia_Formatado', 'Contagem de Nr.NF', 'Pedido Diarios', 'Pendente de Produção', 'Soma de Qtd Total SKU', 'Contagem de SKU']],
        use_container_width=True
    )
