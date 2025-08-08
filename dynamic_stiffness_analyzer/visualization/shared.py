from __future__ import annotations

import plotly.graph_objects as go
from dash import html


def generar_figura_vacia(titulo: str = "Sin datos") -> go.Figure:
    fig = go.Figure()
    fig.update_layout(title="Sin datos disponibles", paper_bgcolor='#111111', plot_bgcolor='#111111', font=dict(color='white'))
    return fig


def generar_graficos_vacios():
    fig_vacio = go.Figure()
    fig_vacio.update_layout(title="Sin datos disponibles", paper_bgcolor='#111111', plot_bgcolor='#111111', font=dict(color='white'))
    return (fig_vacio, fig_vacio, fig_vacio, html.Div(), fig_vacio, fig_vacio, [], [], False, {'backgroundColor': '#7C8085', 'color': 'white', 'fontWeight': 'bold', 'borderRadius': '4px', 'border': 'none', 'padding': '8px 15px'}, 5, 0.5, '')



