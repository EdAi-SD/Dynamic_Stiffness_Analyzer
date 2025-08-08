from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def generar_grafico_rigidez(f_plot: np.ndarray, magK: np.ndarray, phase_plot: np.ndarray, seleccion_eje: str, escala_x: str, escala_y: str) -> go.Figure:
    color_map = {'accel_x': 'red', 'accel_y': 'green', 'accel_z': 'blue'}
    label_map = {'accel_x': 'X', 'accel_y': 'Y', 'accel_z': 'Z'}
    mag_plot_mm = magK / 1000.0
    if escala_y == 'db':
        y_plot = 20 * np.log10(np.maximum(mag_plot_mm, 1e-10))
        yaxis_title = '|K| (dB N/mm)'
    else:
        y_plot = mag_plot_mm
        yaxis_title = '(N/mm)'

    indicador_frf = 'Hv'
    fig_disp = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.15, subplot_titles=(f'|K|', 'Fase (°)'))
    if escala_y == 'db':
        fig_disp.add_trace(go.Scatter(x=f_plot, y=y_plot, mode='lines', name=f'|K| {label_map.get(seleccion_eje, seleccion_eje)} (dB)', line=dict(color=color_map.get(seleccion_eje, 'gray'))), row=1, col=1)
    else:
        fig_disp.add_trace(go.Scatter(x=f_plot, y=y_plot, mode='lines', name=f'|K| {label_map.get(seleccion_eje, seleccion_eje)}', line=dict(color=color_map.get(seleccion_eje, 'gray'))), row=1, col=1)
    fig_disp.add_trace(go.Scatter(x=f_plot, y=phase_plot, mode='lines', name=f'∠K {label_map.get(seleccion_eje, seleccion_eje)}', line=dict(color=color_map.get(seleccion_eje, 'gray'), dash='dash')), row=2, col=1)
    if len(f_plot) > 0:
        min_f_plot = np.min(f_plot)
        max_f_plot = np.max(f_plot)
        fig_disp.update_xaxes(range=[min_f_plot, max_f_plot], row=1, col=1)
        fig_disp.update_xaxes(range=[min_f_plot, max_f_plot], row=2, col=1)
    ydata = np.array(y_plot)
    if ydata.size > 0 and np.any(np.isfinite(ydata)):
        ymin = np.nanmin(ydata)
        ymax = np.nanmax(ydata)
        if np.isfinite(ymin) and np.isfinite(ymax):
            margen = 0.05 * (ymax - ymin) if ymax > ymin else 1
            fig_disp.update_yaxes(range=[ymin - margen, ymax + margen], row=1, col=1)
    ydata_phase = np.array(phase_plot)
    if ydata_phase.size > 0 and np.any(np.isfinite(ydata_phase)):
        ymin_p = np.nanmin(ydata_phase)
        ymax_p = np.nanmax(ydata_phase)
        if np.isfinite(ymin_p) and np.isfinite(ymax_p):
            margen_p = 0.05 * (ymax_p - ymin_p) if ymax_p > ymin_p else 1
            fig_disp.update_yaxes(range=[ymin_p - margen_p, ymax_p + margen_p], row=2, col=1)
    fig_disp.update_layout(title_text=f'Rigidez Dinámica {indicador_frf} ({label_map.get(seleccion_eje, seleccion_eje)})',
                           xaxis=dict(title='Frecuencia (Hz)', type=escala_x), yaxis=dict(title=yaxis_title),
                           yaxis2=dict(title='Fase (°)'), paper_bgcolor='#111111', plot_bgcolor='#111111',
                           font=dict(color='white'), height=600)
    fig_disp.update_xaxes(title_text='Frecuencia (Hz)', row=2, col=1)
    fig_disp.update_xaxes(showticklabels=True, row=1, col=1)
    return fig_disp



