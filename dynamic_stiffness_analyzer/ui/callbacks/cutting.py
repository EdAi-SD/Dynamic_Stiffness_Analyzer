from __future__ import annotations

from dash import Output, Input, State, no_update, ctx
import pandas as pd

from app_legacy import app
from dynamic_stiffness_analyzer.signal_processing.cutting import aplicar_corte_df


def _output_exists(component_id: str, prop: str) -> bool:
    key = f"{component_id}.{prop}"
    try:
        return key in getattr(app, "callback_map", {})
    except Exception:
        return False


if not getattr(app, "_callbacks_cutting_registered", False):
    if not _output_exists('store-df-corte', 'data'):
        @app.callback(
            Output('store-df-corte', 'data'),
            Output('mensaje-corte', 'children'),
            Input('boton-aplicar-corte', 'n_clicks'),
            State('input-corte-inicio', 'value'),
            State('input-corte-fin', 'value'),
            State('store-df-filtrado', 'data'),
            State('store-df', 'data'),
            State('selector-multi', 'value'),
            prevent_initial_call=True,
        )
        def aplicar_corte(n_clicks, inicio, fin, df_filtrado_json, df_json, senales_seleccionadas):
            if n_clicks is None or (df_filtrado_json is None and df_json is None):
                return no_update, ''
            try:
                df = pd.read_json(df_filtrado_json or df_json, orient='split')
            except Exception:
                return no_update, 'Datos inválidos.'
            try:
                df_corte, mensaje = aplicar_corte_df(df, inicio, fin, senales_seleccionadas)
                return df_corte.to_json(date_format='iso', orient='split'), mensaje
            except Exception as e:
                return no_update, str(e)

    # Estado visual del botón de corte
    if not _output_exists('boton-aplicar-corte', 'disabled'):
        @app.callback(
            Output('boton-aplicar-corte', 'disabled'),
            Output('boton-aplicar-corte', 'style'),
            Output('icono-corte', 'children'),
            Output('icono-corte', 'style'),
            Input('store-df', 'data'),
            Input('store-df-filtrado', 'data'),
            Input('input-corte-inicio', 'value'),
            Input('input-corte-fin', 'value'),
            Input('boton-aplicar-corte', 'n_clicks'),
            prevent_initial_call=True,
        )
        def controlar_estado_corte(df_json, df_filtrado_json, inicio, fin, n_clicks_corte):
            ctx_triggered = ctx.triggered_id if hasattr(ctx, 'triggered_id') else None
            if df_json is None:
                return True, {'marginLeft': '30px', 'backgroundColor': '#6c757d', 'color': 'white', 'fontWeight': 'bold', 'borderRadius': '4px', 'border': 'none', 'padding': '8px 15px'}, '⚠', {'marginRight': '5px', 'fontSize': '16px', 'color': '#ffc107'}
            if ctx_triggered == 'boton-aplicar-corte' and n_clicks_corte > 0:
                return True, {'marginLeft': '30px', 'backgroundColor': '#ffc107', 'color': 'white', 'fontWeight': 'bold', 'borderRadius': '4px', 'border': 'none', 'padding': '8px 15px'}, '⏳', {'marginRight': '5px', 'fontSize': '16px', 'color': 'white'}
            if inicio is None or fin is None or inicio >= fin:
                return True, {'marginLeft': '30px', 'backgroundColor': '#6c757d', 'color': 'white', 'fontWeight': 'bold', 'borderRadius': '4px', 'border': 'none', 'padding': '8px 15px'}, '○', {'marginRight': '5px', 'fontSize': '16px', 'color': '#ffc107'}
            if n_clicks_corte > 0:
                return True, {'marginLeft': '30px', 'backgroundColor': '#28a745', 'color': 'white', 'fontWeight': 'bold', 'borderRadius': '4px', 'border': 'none', 'padding': '8px 15px'}, '✓', {'marginRight': '5px', 'fontSize': '16px', 'color': 'white'}
            else:
                return False, {'marginLeft': '30px', 'backgroundColor': '#17a2b8', 'color': 'white', 'fontWeight': 'bold', 'borderRadius': '4px', 'border': 'none', 'padding': '8px 15px'}, '◯', {'marginRight': '5px', 'fontSize': '16px', 'color': 'white'}

    setattr(app, "_callbacks_cutting_registered", True)


