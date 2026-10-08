import pandas as pd

def obter_kpis_gerais(df_prod, df_sep):
    """
    Calcula os KPIs consolidados para os cards executivos.
    """
    if df_prod is None or df_prod.empty:
        return 0, 0.0, 0, 0.0

    total_nfs = df_prod['nfs_emitidas'].sum()
    media_nfs_dia = df_prod['nfs_emitidas'].mean()
    
    total_pecas_skus = df_sep['qtd_skus'].sum() if df_sep is not None else 0
    media_backlog_dia = df_prod['pendente_producao'].mean()
    
    return int(total_nfs), media_nfs_dia, int(total_pecas_skus), media_backlog_dia