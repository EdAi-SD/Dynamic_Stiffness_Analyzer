from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.fft import rfft, rfftfreq
from scipy.signal import get_window

from dynamic_stiffness_analyzer.config.settings import CONFIG
from dynamic_stiffness_analyzer.signal_processing.windowing import ventana_exponencial, ventana_fuerza_adaptativa


def generar_grafico_fft_optimizado(df: pd.DataFrame, seleccion_multi, escala_x: str, escala_y: str) -> go.Figure:
    fig_fft = go.Figure()
    if df is None or df.empty:
        return fig_fft
    t = df['tiempo'].values
    if len(t) < 2:
        return fig_fft
    dt_values = np.diff(t)
    dt_values_valid = dt_values[dt_values > 0]
    if len(dt_values_valid) == 0:
        return fig_fft
    dt = np.median(dt_values_valid)
    if dt <= 0 or not np.isfinite(dt):
        dt = (t[-1] - t[0]) / (len(t) - 1) if len(t) > 1 else 0.001
        if dt <= 0:
            dt = 0.001
    fs = 1 / dt
    for col in seleccion_multi:
        if col not in df.columns:
            continue
        y = df[col].values
        if len(y) == 0 or not np.isfinite(y).any():
            continue
        try:
            if col.startswith('accel_'):
                y_proc = ventana_exponencial(y, fs)
            elif col.startswith('fuerza'):
                y_proc = ventana_fuerza_adaptativa(y, fs)
            else:
                y_proc = y
        except Exception:
            y_proc = y
        N = len(y_proc)
        if N < 4:
            continue
        try:
            yf = rfft(y_proc * get_window('hann', N))
            xf = rfftfreq(N, dt)
            amp = np.abs(yf)
            if escala_y == 'db':
                amp = 20 * np.log10(np.maximum(amp, 1e-12))
                amp = np.where(np.isfinite(amp), amp, -240)
            if len(xf) > CONFIG.VISUALIZACION['MAX_PUNTOS_FFT']:
                step_visual = max(1, len(xf) // CONFIG.VISUALIZACION['REDUCCION_VISUAL_FFT'])
                xf_visual = xf[::step_visual]
                amp_visual = amp[::step_visual]
            else:
                xf_visual = xf
                amp_visual = amp
            fig_fft.add_trace(go.Scatter(x=xf_visual, y=amp_visual, mode='lines', name=col))
        except Exception:
            continue
    titulo = f'Dominio de la Frecuencia (FFT) (Optimizada para {len(df):,} puntos) - fs={fs:.1f} Hz'
    fig_fft.update_layout(title=titulo, xaxis_title='Frecuencia (Hz)',
                          yaxis_title='Amplitud (dB)' if escala_y == 'db' else 'Amplitud (g)', xaxis_type=escala_x,
                          paper_bgcolor='#111111', plot_bgcolor='#111111', font=dict(color='white'))
    return fig_fft



