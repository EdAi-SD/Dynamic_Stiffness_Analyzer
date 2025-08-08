from __future__ import annotations

import numpy as np
import plotly.graph_objects as go


def generar_grafico_coherencia(fK: np.ndarray, S_ff, S_xx, S_xf) -> go.Figure:
    fig = go.Figure()
    try:
        coh_debug = np.abs(S_xf) ** 2 / (S_ff * S_xx + 1e-12)
        if coh_debug.size > 0 and np.isfinite(coh_debug).any():
            valid_coh = np.isfinite(coh_debug) & np.isfinite(fK)
            if np.any(valid_coh):
                fig.add_trace(go.Scatter(x=fK[valid_coh], y=coh_debug[valid_coh], mode='lines+markers', name='Coherencia', line=dict(color='orange')))
    except Exception:
        pass
    fig.update_layout(title='Coherencia FRF (Hv)', xaxis_title='Frecuencia (Hz)', yaxis_title='Coherencia',
                      yaxis=dict(range=[0, 1.05]), paper_bgcolor='#111111', plot_bgcolor='#111111',
                      font=dict(color='white'), height=350, margin=dict(l=80, r=60, t=80, b=160))
    return fig



