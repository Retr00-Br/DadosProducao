import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

BG_CARD = "#1C2541"
TEXT_WHITE = "#FFFFFF"
COLOR_PRIMARY = "#00B4D8"
COLOR_SECONDARY = "#90E0EF"
COLOR_ALERT = "#FF4D6D"
COLOR_SUCCESS = "#38B000"

LAYOUT_THEME = dict(
    paper_bgcolor=BG_CARD,
    plot_bgcolor=BG_CARD,
    font=dict(color=TEXT_WHITE, family="Sans-serif", size=12),
    xaxis=dict(gridcolor="#1E293B", showgrid=True, tickfont=dict(color=TEXT_WHITE)),
    yaxis=dict(gridcolor="#1E293B", showgrid=True, tickfont=dict(color=TEXT_WHITE)),
    margin=dict(l=30, r=20, t=40, b=40),
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
    hoverlabel=dict(bgcolor="#0A1128", font_color=TEXT_WHITE)
)

def criar_grafico_nfs_meta(df_prod, meta_diaria=120):
    fig = go.Figure()
    
    df_prod['data_str'] = df_prod['data'].astype(str)
    
    fig.add_trace(go.Bar(
        x=df_prod['data_str'],
        y=df_prod['nfs_emitidas'],
        name="NFs Emitidas",
        marker_color=COLOR_PRIMARY
    ))
    
    fig.add_trace(go.Scatter(
        x=df_prod['data_str'],
        y=[meta_diaria] * len(df_prod),
        mode='lines',
        name=f"Meta ({meta_diaria})",
        line=dict(color=COLOR_ALERT, dash='dash', width=2)
    ))
    
    fig.update_layout(**LAYOUT_THEME, height=360)
    return fig

def criar_grafico_volume_pecas(df_sep):
    df_group = df_sep.groupby('data')['qtd_skus'].sum().reset_index()
    df_group['data_str'] = df_group['data'].astype(str)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_group['data_str'],
        y=df_group['qtd_skus'],
        mode='lines+markers',
        name="Peças Processadas (SKUs)",
        line=dict(color=COLOR_SECONDARY, width=3),
        marker=dict(size=6, color=COLOR_PRIMARY),
        fill='tozeroy',
        fillcolor='rgba(0, 180, 216, 0.15)'
    ))
    
    fig.update_layout(**LAYOUT_THEME, height=360)
    return fig

def criar_grafico_backlogs_realizados(df_sep):
    df_group = df_sep.groupby('data')['backlog_realizado'].sum().reset_index()
    df_group['data_str'] = df_group['data'].astype(str)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_group['data_str'],
        y=df_group['backlog_realizado'],
        name="Backlogs Realizados (Faturados)",
        marker_color=COLOR_SUCCESS
    ))
    
    fig.update_layout(**LAYOUT_THEME, height=360)
    return fig

def criar_grafico_ranking_separadores_nfs(df_sep, top_n=10):
    df_rank = df_sep.groupby('separador')['nr_nf'].nunique().reset_index()
    df_rank = df_rank.sort_values('nr_nf', ascending=True).tail(top_n)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_rank['nr_nf'],
        y=df_rank['separador'],
        orientation='h',
        marker_color=COLOR_PRIMARY,
        name="NFs Distintas"
    ))
    fig.update_layout(**LAYOUT_THEME, height=400)
    return fig

def criar_grafico_ranking_separadores_skus(df_sep, top_n=10):
    df_rank = df_sep.groupby('separador')['qtd_skus'].sum().reset_index()
    df_rank = df_rank.sort_values('qtd_skus', ascending=True).tail(top_n)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_rank['qtd_skus'],
        y=df_rank['separador'],
        orientation='h',
        marker_color=COLOR_SECONDARY,
        name="Peças / SKUs"
    ))
    fig.update_layout(**LAYOUT_THEME, height=400)
    return fig