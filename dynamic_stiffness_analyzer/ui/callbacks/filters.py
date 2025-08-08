from __future__ import annotations

from dash import Output, Input, State, no_update, html, ctx
import pandas as pd
import numpy as np

from app_legacy import app
from dynamic_stiffness_analyzer.config.settings import CONFIG
from dynamic_stiffness_analyzer.signal_processing.filters import filtrar_senal


def _output_exists(component_id: str, prop: str) -> bool:
    key = f"{component_id}.{prop}"
    try:
        return key in getattr(app, "callback_map", {})
    except Exception:
        return False


if not getattr(app, "_callbacks_filters_registered", False):
    # Deshabilitar inputs de parámetros de filtros según toggles
    if not _output_exists('input-mediana', 'disabled'):
        @app.callback(
            Output('input-mediana', 'disabled'),
            Output('input-highpass', 'disabled'),
            Output('input-bandpass-multibanda', 'disabled'),
            Input('toggle-mediana', 'value'),
            Input('toggle-highpass', 'value'),
            Input('toggle-bandpass', 'value'),
        )
        def deshabilitar_inputs_filtros(toggle_mediana, toggle_highpass, toggle_bandpass):
            return (
                toggle_mediana != 'yes',
                toggle_highpass != 'yes',
                toggle_bandpass != 'yes',
            )

    # Limites min/max del input de duración de segmento
    if not _output_exists('input-duracion-segmento', 'min'):
        @app.callback(
            Output('input-duracion-segmento', 'min'),
            Output('input-duracion-segmento', 'max'),
            Input('store-df', 'data'),
            Input('store-df-corte', 'data'),
            Input('store-df-filtrado', 'data'),
        )
        def actualizar_limites_duracion_segmento(df_json, df_corte_json, df_filtrado_json):
            min_val = CONFIG.TOLERANCIAS['MIN_DURACION_SEGMENTO']
            max_val = 9999
            df_base = None
            if df_corte_json:
                df_base = pd.read_json(df_corte_json, orient='split')
            elif df_filtrado_json:
                df_base = pd.read_json(df_filtrado_json, orient='split')
            elif df_json:
                df_base = pd.read_json(df_json, orient='split')
            if df_base is not None and 'tiempo' in df_base.columns:
                t = df_base['tiempo'].values
                if len(t) > 1:
                    dt = np.median(np.diff(t))
                    fs = 1 / dt
                    min_window = CONFIG.VENTANAS_WATERFALL['MINIMO']
                    min_val = round(min_window / fs, 2)
                    duracion_total = t[-1] - t[0]
                    max_val = max(min_val, round(float(duracion_total), 2))
            return min_val, max_val

    # Sincronizar valor dentro del rango permitido
    if not _output_exists('input-duracion-segmento', 'value'):
        @app.callback(
            Output('input-duracion-segmento', 'value'),
            Input('input-duracion-segmento', 'min'),
            Input('input-duracion-segmento', 'max'),
            State('input-duracion-segmento', 'value'),
        )
        def sincronizar_valor_duracion_segmento(min_val, max_val, valor_actual):
            min_val = round(float(min_val), 2)
            max_val = round(float(max_val), 2)
            if valor_actual is None:
                return min_val
            valor_actual = round(float(valor_actual), 2)
            if valor_actual < min_val:
                return min_val
            elif valor_actual > max_val:
                return max_val
            else:
                return valor_actual

    # Mostrar rango permitido
    if not _output_exists('texto-rango-duracion-segmento', 'children'):
        @app.callback(
            Output('texto-rango-duracion-segmento', 'children'),
            Input('input-duracion-segmento', 'min'),
            Input('input-duracion-segmento', 'max'),
        )
        def mostrar_rango_duracion_segmento(min_val, max_val):
            return f"Rango permitido: {min_val:.2f} s – {max_val:.2f} s"

    # Aplicar filtros
    if not _output_exists('store-df-filtrado', 'data'):
        @app.callback(
            Output('store-df-filtrado', 'data'),
            Output('mensaje-filtro', 'children'),
            Input('boton-aplicar-filtros', 'n_clicks'),
            State('store-df', 'data'),
            State('store-df-corte', 'data'),
            State('selector-multi', 'value'),
            State('selector-eje', 'value'),
            State('input-mediana', 'value'),
            State('input-highpass', 'value'),
            State('input-bandpass-multibanda', 'value'),
            State('toggle-mediana', 'value'),
            State('toggle-highpass', 'value'),
            State('toggle-bandpass', 'value'),
            prevent_initial_call=True,
        )
        def aplicar_filtros(n_clicks, df_json, df_corte_json, seleccion_multi, seleccion_eje, mediana_val, highpass_val,
                            bandpass_multibanda, toggle_mediana, toggle_highpass, toggle_bandpass):
            if n_clicks is None or n_clicks == 0:
                return no_update, no_update
            if df_json is None:
                return None, html.Div("No hay datos para filtrar", style={'color': 'red'})
            try:
                df = pd.read_json(df_json, orient='split')
                if df.empty or 'tiempo' not in df.columns:
                    return None, html.Div("Datos inválidos", style={'color': 'red'})
                t = df['tiempo'].values
                dt = np.median(np.diff(t))
                fs = 1 / dt
                df_filtrado, mensajes_filtro, _ = filtrar_senal(
                    df, seleccion_multi, seleccion_eje, fs, mediana_val, highpass_val,
                    bandpass_multibanda, toggle_mediana, toggle_highpass, toggle_bandpass
                )
                mensaje = html.Div([
                    html.Span("✅ Filtros aplicados correctamente", style={'color': 'green', 'fontWeight': 'bold'}),
                    html.Br(),
                    html.Span(f"Señales procesadas: {len(seleccion_multi or [])}", style={'color': 'white'})
                ])
                return df_filtrado.to_json(orient='split'), mensaje
            except Exception as e:
                print(f"[ERROR] Error aplicando filtros: {e}")
                return None, html.Div(f"Error: {str(e)[:50]}", style={'color': 'red'})

    # Estilo visual del botón de filtros
    if not _output_exists('boton-aplicar-filtros', 'style'):
        @app.callback(
            Output('boton-aplicar-filtros', 'style'),
            Output('icono-filtros', 'children'),
            Output('icono-filtros', 'style'),
            Input('store-df', 'data'),
            Input('store-df-corte', 'data'),
            Input('toggle-mediana', 'value'),
            Input('toggle-highpass', 'value'),
            Input('toggle-bandpass', 'value'),
            Input('boton-aplicar-filtros', 'n_clicks'),
            prevent_initial_call=True,
        )
        def controlar_estilo_filtros(df_json, df_corte_json, toggle_med, toggle_hp, toggle_bp, n_clicks_filtros):
            ctx_triggered = ctx.triggered_id if hasattr(ctx, 'triggered_id') else None
            if df_json is None:
                return {'backgroundColor': '#6c757d', 'color': 'white', 'fontWeight': 'bold', 'borderRadius': '4px', 'border': 'none', 'padding': '8px 15px', 'marginRight': '15px'}, '⚠', {'marginRight': '5px', 'fontSize': '16px', 'color': '#ffc107'}
            if df_corte_json is not None:
                return {'backgroundColor': '#dc3545', 'color': 'white', 'fontWeight': 'bold', 'borderRadius': '4px', 'border': 'none', 'padding': '8px 15px', 'marginRight': '15px'}, '✗', {'marginRight': '5px', 'fontSize': '16px', 'color': 'white'}
            if ctx_triggered == 'boton-aplicar-filtros' and n_clicks_filtros > 0:
                return {'backgroundColor': '#ffc107', 'color': 'white', 'fontWeight': 'bold', 'borderRadius': '4px', 'border': 'none', 'padding': '8px 15px', 'marginRight': '15px'}, '⏳', {'marginRight': '5px', 'fontSize': '16px', 'color': 'white'}
            algun_filtro_activo = (toggle_med == 'yes') or (toggle_hp == 'yes') or (toggle_bp == 'yes')
            if not algun_filtro_activo:
                return {'backgroundColor': '#6c757d', 'color': 'white', 'fontWeight': 'bold', 'borderRadius': '4px', 'border': 'none', 'padding': '8px 15px', 'marginRight': '15px'}, '○', {'marginRight': '5px', 'fontSize': '16px', 'color': '#ffc107'}
            if n_clicks_filtros > 0:
                return {'backgroundColor': '#28a745', 'color': 'white', 'fontWeight': 'bold', 'borderRadius': '4px', 'border': 'none', 'padding': '8px 15px', 'marginRight': '15px'}, '✓', {'marginRight': '5px', 'fontSize': '16px', 'color': 'white'}
            else:
                return {'backgroundColor': '#17a2b8', 'color': 'white', 'fontWeight': 'bold', 'borderRadius': '4px', 'border': 'none', 'padding': '8px 15px', 'marginRight': '15px'}, '◯', {'marginRight': '5px', 'fontSize': '16px', 'color': 'white'}

    # Deshabilitar botón de filtros bajo condiciones
    if not _output_exists('boton-aplicar-filtros', 'disabled'):
        @app.callback(
            Output('boton-aplicar-filtros', 'disabled'),
            Input('store-df-corte', 'data'),
            Input('store-df', 'data'),
            Input('toggle-mediana', 'value'),
            Input('toggle-highpass', 'value'),
            Input('toggle-bandpass', 'value'),
            Input('boton-aplicar-filtros', 'n_clicks'),
            prevent_initial_call=True,
        )
        def deshabilitar_filtro_si_corte(df_corte_json, df_json, toggle_med, toggle_hp, toggle_bp, n_clicks_filtros):
            ctx_triggered = ctx.triggered_id if hasattr(ctx, 'triggered_id') else None
            if ctx_triggered == 'boton-aplicar-filtros' and n_clicks_filtros > 0:
                return True
            if df_corte_json is not None:
                return True
            if df_json is None:
                return True
            algun_filtro_activo = (toggle_med == 'yes') or (toggle_hp == 'yes') or (toggle_bp == 'yes')
            if not algun_filtro_activo:
                return True
            if n_clicks_filtros > 0:
                return True
            return False

    setattr(app, "_callbacks_filters_registered", True)


