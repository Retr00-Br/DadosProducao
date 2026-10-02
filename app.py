import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import datetime
import os

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E PALETA DARK
# ==========================================
st.set_page_config(
    page_title="HIGIMED — Operação & Produção",
    page_icon="🏥",
    layout="wide"
)

# Paleta de Cores HIGIMED - Dark Navy Executivo
BG_MAIN = "#0B132B"         # Fundo Geral Azul Escuro
BG_CARD = "#1C2541"         # Fundo dos Cards e Gráficos
COLOR_PRIMARY = "#00B4D8"   # Azul Cyan Destaque
COLOR_SECONDARY = "#90E0EF" # Azul Claro
TEXT_WHITE = "#FFFFFF"      # Texto Branco Puro
TEXT_MUTED = "#CBD5E1"      # Texto Secundário Claro
COLOR_ALERT = "#FF4D6D"      # Alerta Vermelho Neon
COLOR_SUCCESS = "#38B000"    # Verde Sucesso

# Estilização CSS Personalizada (Textos em Branco Puro e Inputs Customizados)
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
        
        /* Forçar todos os Rótulos e Textos da Barra Lateral em Branco */
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 {{
            color: {TEXT_WHITE} !important;
            font-weight: 600 !important;
        }}
        
        /* Títulos do Painel */
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
            font-size: 0.82rem;
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

# ==========================================
# 2. HEADER DA APLICAÇÃO WITH LOGO
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
    
    # Limpeza de linhas irrelevantes
    df = df[~df['Dias'].astype(str).str.contains('Média|Soma|Total', case=False, na=False)].copy()
    
    # Tratamento de datas
    df['Data_Obj'] = df['Dias'].apply(parse_dia_to_date)
    df = df.dropna(subset=['Data_Obj']).sort_values('Data_Obj')
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
# 4. FILTRO DINÂMICO DE DATAS
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
# 5. CARDS DE KPI EXECUTIVOS
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

# Layout do Tema Plotly Dark
LAYOUT_PLOTLY = dict(
    paper_bgcolor=BG_CARD,
    plot_bgcolor=BG_CARD,
    font=dict(color=TEXT_WHITE, family="Sans-serif"),
    xaxis=dict(gridcolor="#1E293B", tickangle=-45, showgrid=True),
    yaxis=dict(gridcolor="#1E293B", showgrid=True),
    margin=dict(l=40, r=20, t=40, b=50),
    hoverlabel=dict(bgcolor="#0A1128", font_color=TEXT_WHITE, font_size=12)
)

# ==========================================
# 6. GRÁFICOS INTERATIVOS (PLOTLY HOVER)
# ==========================================

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.markdown("##### 🎯 NFs Emitidas vs. Meta Diária (120)")
    
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=df_filtrado['Dia_Formatado'],
        y=df_filtrado['Contagem de Nr.NF'],
        name="NFs Emitidas",
        marker_color=COLOR_PRIMARY,
        hovertemplate="<b>Data:</b> %{x}<br><b>NFs Emitidas:</b> %{y}<extra></extra>"
    ))
    fig1.add_trace(go.Scatter(
        x=df_filtrado['Dia_Formatado'],
        y=[120] * len(df_filtrado),
        mode='lines',
        name="Meta Diária (120)",
        line=dict(color=COLOR_ALERT, dash='dash', width=2),
        hovertemplate="<b>Meta:</b> 120 NFs<extra></extra>"
    ))
    fig1.update_layout(**LAYOUT_PLOTLY, height=380, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig1, use_container_width=True)

with col_graf2:
    st.markdown("##### 📦 Volume Total de Peças Processadas por Dia")
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_filtrado['Dia_Formatado'],
        y=df_filtrado['Soma de Qtd Total SKU'],
        mode='lines+markers',
        name="Qtd Peças",
        line=dict(color=COLOR_SECONDARY, width=3),
        marker=dict(size=6, color=COLOR_PRIMARY),
        fill='tozeroy',
        fillcolor='rgba(0, 180, 216, 0.15)',
        hovertemplate="<b>Data:</b> %{x}<br><b>Peças Processadas:</b> %{y:,.0f}<extra></extra>"
    ))
    fig2.update_layout(**LAYOUT_PLOTLY, height=380)
    st.plotly_chart(fig2, use_container_width=True)

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    st.markdown("##### ⏳ Saldo de Pendência de Produção Diária")
    
    cores_pend = [COLOR_ALERT if x > 0 else COLOR_SUCCESS for x in df_filtrado['Pendente de Produção']]
    
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=df_filtrado['Dia_Formatado'],
        y=df_filtrado['Pendente de Produção'],
        marker_color=cores_pend,
        hovertemplate="<b>Data:</b> %{x}<br><b>Pendência:</b> %{y} pedidos<extra></extra>"
    ))
    fig3.update_layout(**LAYOUT_PLOTLY, height=380)
    st.plotly_chart(fig3, use_container_width=True)

with col_graf4:
    st.markdown("##### 🏷️ Diversidade de SKUs Únicos Movimentados por Dia")
    
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=df_filtrado['Dia_Formatado'],
        y=df_filtrado['Contagem de SKU'],
        marker_color=COLOR_SECONDARY,
        hovertemplate="<b>Data:</b> %{x}<br><b>SKUs Distintos:</b> %{y}<extra></extra>"
    ))
    fig4.update_layout(**LAYOUT_PLOTLY, height=380)
    st.plotly_chart(fig4, use_container_width=True)

# Tabela Interativa
with st.expander("📄 Visualizar Tabela Tratada da Operação"):
    st.dataframe(
        df_filtrado[['Data_Obj', 'Dia_Formatado', 'Contagem de Nr.NF', 'Pedido Diarios', 'Pendente de Produção', 'Soma de Qtd Total SKU', 'Contagem de SKU']],
        use_container_width=True
    )
