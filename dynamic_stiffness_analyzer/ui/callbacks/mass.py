from __future__ import annotations

from dash import Output, Input, State, no_update, ctx

from app_legacy import app
from dynamic_stiffness_analyzer.services.validation import (
    validar_masa_martillo as _validar_masa_martillo,
)


def validar_masa_martillo(masa):
    return _validar_masa_martillo(masa)


def _output_exists(component_id: str, prop: str) -> bool:
    key = f"{component_id}.{prop}"
    try:
        return key in getattr(app, "callback_map", {})
    except Exception:
        return False


if not getattr(app, "_callbacks_mass_registered", False):
    if not _output_exists('mensaje-masa-martillo', 'children'):
        @app.callback(
            Output('mensaje-masa-martillo', 'children'),
            Input('boton-aplicar-masa', 'n_clicks'),
            Input('input-masa-martillo', 'value'),
            State('input-masa-martillo', 'value'),
            prevent_initial_call=True,
        )
        def actualizar_mensaje_masa(n_clicks_boton, masa_input, masa_state):
            trigger_id = ctx.triggered_id if hasattr(ctx, 'triggered_id') else None
            if trigger_id == 'boton-aplicar-masa' and n_clicks_boton > 0:
                masa_validada, _ = validar_masa_martillo(masa_state)
                return f"✓ Masa aplicada: {masa_validada} kg - Los cálculos se actualizarán automáticamente"
            elif trigger_id == 'input-masa-martillo':
                _, mensaje = validar_masa_martillo(masa_input)
                return f"⚠ {mensaje} - Haga clic en 'Aplicar masa' para confirmar"
            return ""

    if not _output_exists('boton-aplicar-masa', 'disabled'):
        @app.callback(
            Output('boton-aplicar-masa', 'disabled'),
            Output('boton-aplicar-masa', 'style'),
            Output('icono-masa', 'children'),
            Output('icono-masa', 'style'),
            Input('store-df', 'data'),
            Input('input-masa-martillo', 'value'),
            Input('boton-aplicar-masa', 'n_clicks'),
            prevent_initial_call=True,
        )
        def controlar_estado_masa(df_json, masa_valor, n_clicks_masa):
            ctx_triggered = ctx.triggered_id if hasattr(ctx, 'triggered_id') else None
            if df_json is None:
                return True, {'backgroundColor': '#6c757d', 'color': 'white', 'fontWeight': 'bold', 'borderRadius': '4px', 'border': 'none', 'padding': '8px 15px', 'marginRight': '15px'}, '⚠', {'marginRight': '5px', 'fontSize': '16px', 'color': '#ffc107'}
            if ctx_triggered == 'boton-aplicar-masa' and n_clicks_masa > 0:
                return True, {'backgroundColor': '#ffc107', 'color': 'white', 'fontWeight': 'bold', 'borderRadius': '4px', 'border': 'none', 'padding': '8px 15px', 'marginRight': '15px'}, '⏳', {'marginRight': '5px', 'fontSize': '16px', 'color': 'white'}
            masa_validada, _ = validar_masa_martillo(masa_valor)
            if n_clicks_masa > 0 and masa_validada == masa_valor:
                return True, {'backgroundColor': '#28a745', 'color': 'white', 'fontWeight': 'bold', 'borderRadius': '4px', 'border': 'none', 'padding': '8px 15px', 'marginRight': '15px'}, '✓', {'marginRight': '5px', 'fontSize': '16px', 'color': 'white'}
            else:
                return False, {'backgroundColor': '#17a2b8', 'color': 'white', 'fontWeight': 'bold', 'borderRadius': '4px', 'border': 'none', 'padding': '8px 15px', 'marginRight': '15px'}, '◯', {'marginRight': '5px', 'fontSize': '16px', 'color': 'white'}

    setattr(app, "_callbacks_mass_registered", True)


