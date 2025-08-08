from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from dynamic_stiffness_analyzer.config.settings import CONFIG


def optimizar_dataframe_para_visualizacion(df: pd.DataFrame, max_puntos: int = 50000):
    if df is None or len(df) <= max_puntos:
        return df, False
    n_total = len(df)
    primer_10_pct = n_total // 10
    puntos_inicio = int(max_puntos * 0.3)
    step_inicio = max(1, primer_10_pct // max(puntos_inicio, 1))
    puntos_resto = max_puntos - puntos_inicio
    step_resto = max(1, (n_total - primer_10_pct) // max(puntos_resto, 1))
    indices = list(range(0, primer_10_pct, step_inicio))
    indices += list(range(primer_10_pct, n_total, step_resto))
    indices = sorted(set(indices))
    if indices[-1] != n_total - 1:
        indices.append(n_total - 1)
    return df.iloc[indices].copy().reset_index(drop=True), True


def generar_grafico_tiempo_optimizado(df: pd.DataFrame, seleccion_multi, df_original=None, filtro_aplicado=False, df_corte_json=None):
    df_viz, optimizado = optimizar_dataframe_para_visualizacion(df, max_puntos=CONFIG.VISUALIZACION['MAX_PUNTOS_TIEMPO'])
    fig_tiempo = go.Figure()
    t = df_viz['tiempo'].values
    colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    for i, col in enumerate(seleccion_multi):
        color = colores[i % len(colores)]
        if filtro_aplicado and df_original is not None and col in df_original.columns and not df_corte_json:
            df_orig_viz, _ = optimizar_dataframe_para_visualizacion(df_original, max_puntos=CONFIG.VISUALIZACION['MAX_PUNTOS_TIEMPO'])
            fig_tiempo.add_trace(go.Scatter(x=df_orig_viz['tiempo'].values, y=df_orig_viz[col].values, mode='lines',
                                            name=col + '(original)', line=dict(dash='dot', color='gray')))
        if col in df_viz.columns:
            nombre = col + (' (filtrada)' if filtro_aplicado else '')
            fig_tiempo.add_trace(go.Scatter(x=t, y=df_viz[col].values, mode='lines', name=nombre, line=dict(color=color)))
    titulo = 'Dominio del Tiempo'
    if optimizado:
        titulo += f' (Visualización optimizada: {len(df_viz):,}/{len(df):,} puntos)'
    fig_tiempo.update_layout(title=titulo, xaxis_title='Tiempo (s)', yaxis_title='Amplitud (g)',
                              paper_bgcolor='#111111', plot_bgcolor='#111111', font=dict(color='white'))
    return fig_tiempo



