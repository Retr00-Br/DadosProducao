import pandas as pd
import numpy as np
import datetime

def calcular_previsao_demanda(df_prod, dias_previsao=5):
    """
    Aplica modelo de regressão para estimar volume de NFs para os próximos dias operacionais.
    """
    if df_prod is None or df_prod.empty:
        return pd.DataFrame()

    df = df_prod.sort_values('data').copy()
    df['dias_idx'] = np.arange(len(df))
    
    # Ajuste de tendência linear
    x = df['dias_idx'].values
    y = df['nfs_emitidas'].values
    
    if len(x) < 2:
        return pd.DataFrame()
        
    poly = np.polyfit(x, y, deg=1)
    
    ult_idx = x[-1]
    ult_data = df['data'].max()
    
    datas_futuras = []
    previsoes = []
    
    for i in range(1, dias_previsao + 1):
        prox_data = ult_data + datetime.timedelta(days=i)
        pred_y = poly[0] * (ult_idx + i) + poly[1]
        
        datas_futuras.append(prox_data)
        previsoes.append(max(0, round(pred_y, 1)))
        
    df_forecast = pd.DataFrame({
        'data': datas_futuras,
        'previsao_nfs': previsoes,
        'margem_erro_min': [round(p * 0.9, 1) for p in previsoes],
        'margem_erro_max': [round(p * 1.1, 1) for p in previsoes]
    })
    
    return df_forecast