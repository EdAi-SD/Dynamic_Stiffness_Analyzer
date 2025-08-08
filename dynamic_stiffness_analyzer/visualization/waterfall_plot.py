from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.fft import rfft, rfftfreq
from scipy.signal import get_window

from dynamic_stiffness_analyzer.config.settings import CONFIG


def generar_waterfall_adaptativo(df_json: str, seleccion_eje: str, escala_x: str, escala_y: str, curvas_enfasis, estado_fijar_vista: bool, duracion_segmento: float | None):
    if df_json is None or df_json == '':
        return go.Figure(), []
    df_actual = pd.read_json(df_json, orient='split')
    if df_actual.empty or seleccion_eje not in df_actual.columns:
        return go.Figure(), []
    t = df_actual['tiempo'].values
    y_wf = df_actual[seleccion_eje].values
    if len(t) < 2 or len(y_wf) < 2:
        return go.Figure(), []

    dt_values = np.diff(t)
    dt_valid = dt_values[dt_values > 0]
    if len(dt_valid) == 0:
        dt = 0.001
    else:
        dt_median = np.median(dt_valid)
        if dt_median <= 0 or not np.isfinite(dt_median):
            dt = (t[-1] - t[0]) / (len(t) - 1) if len(t) > 1 else 0.001
        else:
            dt = dt_median
    fs = 1 / dt
    N = len(y_wf)
    nyquist_freq = fs / 2

    min_window = CONFIG.TOLERANCIAS['MIN_DURACION_SEGMENTO']
    if duracion_segmento is not None and duracion_segmento > 0:
        window_len = int(max(duracion_segmento, min_window) * fs)
    else:
        window_len = int(min_window * fs)
    window_len = min(window_len, N)
    overlap = 0.5
    step = max(1, int(window_len * (1 - overlap)))
    segment_starts = list(range(0, N - window_len + 1, step))
    if len(segment_starts) > CONFIG.UMBRALES_DATOS['MAX_SEGMENTOS']:
        indices = np.linspace(0, len(segment_starts) - 1, CONFIG.UMBRALES_DATOS['MAX_SEGMENTOS'], dtype=int)
        segment_starts = [segment_starts[i] for i in indices]

    segments_data = []
    fig_waterfall = go.Figure()
    for i, start in enumerate(segment_starts):
        end = min(start + window_len, N)
        actual_len = end - start
        if actual_len < 512:
            continue
        seg = y_wf[start:end]
        window = get_window('hann', actual_len)
        seg_windowed = seg * window
        Z = np.abs(rfft(seg_windowed))
        freqs = rfftfreq(actual_len, dt)
        if not np.isfinite(Z).any() or len(Z) == 0:
            continue
        if escala_y == 'db':
            Z_plot = 20 * np.log10(np.maximum(Z, 1e-12))
        else:
            Z_plot = Z
        tiempo_central = t[start + actual_len // 2]
        freqs_plot = freqs
        Z_plot_final = Z_plot

        if not curvas_enfasis or str(i) in curvas_enfasis:
            line_width = 6
            opacity = 1.0
        else:
            line_width = 1
            opacity = 0.08

        colorscale_geologico = [[0.0, '#000080'], [0.1, '#0000FF'], [0.2, '#0080FF'], [0.3, '#00FFFF'], [0.4, '#00FF80'], [0.5, '#00FF00'], [0.6, '#80FF00'], [0.7, '#FFFF00'], [0.8, '#FF8000'], [0.9, '#FF4000'], [1.0, '#FF0000']]
        fig_waterfall.add_trace(go.Scatter3d(
            x=list(freqs_plot), y=[float(tiempo_central)] * len(freqs_plot), z=list(Z_plot_final),
            mode='lines', line=dict(color=list(Z_plot_final), colorscale=colorscale_geologico, width=line_width),
            opacity=opacity, showlegend=False
        ))

        step_export = max(1, len(freqs_plot) // 2000)
        for j in range(0, len(freqs_plot), step_export):
            if j < len(freqs_plot):
                f, z = freqs_plot[j], Z_plot_final[j]
                if np.isfinite(f) and np.isfinite(z):
                    segments_data.append({'segmento': i + 1, 'tiempo_central': tiempo_central, 'frecuencia': f, 'amplitud': z})

    if estado_fijar_vista:
        camera = dict(eye=dict(x=2.5, y=0, z=0), up=dict(x=0, y=0, z=1), center=dict(x=0, y=0, z=0), projection=dict(type="orthographic"))
        fig_waterfall.update_layout(title="Waterfall 2D (Vista fijada)", scene=dict(
            xaxis_title='Frecuencia (Hz)', yaxis_title='Tiempo (s)', zaxis_title='Amplitud (g)' if escala_y != 'db' else 'Amplitud (dB)',
            xaxis=dict(color='white', backgroundcolor='#111111', showbackground=True), yaxis=dict(color='white', backgroundcolor='#111111', showbackground=True), zaxis=dict(color='white', backgroundcolor='#111111', showbackground=True), camera=camera
        ), paper_bgcolor='#111111', font=dict(color='white'))
    else:
        camera = dict(eye=dict(x=1.2, y=1.2, z=0.8), up=dict(x=0, y=0, z=1), center=dict(x=0, y=0, z=0), projection=dict(type="perspective"))
        scene_config = dict(
            xaxis=dict(title="Frecuencia (Hz)", type=escala_x, color='white', backgroundcolor='black', gridcolor='white', showbackground=True, showgrid=True, zeroline=True, zerolinecolor='white'),
            yaxis=dict(title="Tiempo (s)", color='white', backgroundcolor='black', gridcolor='white', showbackground=True, showgrid=True, zeroline=True, zerolinecolor='white'),
            zaxis=dict(title="Amplitud" + (" (dB)" if escala_y == 'db' else " (g)"), color='white', backgroundcolor='black', gridcolor='white', showbackground=True, showgrid=True, zeroline=True, zerolinecolor='white'),
            camera=camera
        )
        titulo = f'Waterfall 3D - Rango: 0-{nyquist_freq:.0f} Hz ({len(segment_starts)} segmentos) - fs={fs:.0f} Hz'
        fig_waterfall.update_layout(title=dict(text=titulo, font=dict(color='white', size=16)), scene=scene_config,
                                    paper_bgcolor='#111111', plot_bgcolor='black', font=dict(color='white'), margin=dict(l=0, r=0, t=50, b=0))
    return fig_waterfall, segments_data



