from __future__ import annotations

from dash import Output, Input, no_update, html
import threading
import time
import os

from app_legacy import app


def _output_exists(component_id: str, prop: str) -> bool:
    key = f"{component_id}.{prop}"
    try:
        return key in getattr(app, "callback_map", {})
    except Exception:
        return False


if not getattr(app, "_callbacks_control_registered", False):
    if not _output_exists('estado-cierre', 'data'):
    @app.callback(Output('estado-cierre', 'data'), Input('boton-cerrar-app', 'n_clicks'), prevent_initial_call=True)
    def activar_cierre(n_clicks):
        if n_clicks:
            return True
        return no_update


    if not _output_exists('overlay-cierre', 'children'):
        @app.callback(Output('overlay-cierre', 'children'), Input('estado-cierre', 'data'))
        def mostrar_overlay_cierre(estado):
            if estado:
                return html.Div([
                    html.Div([
                        html.H2("La aplicación se cerrará en un momento...", style={'marginBottom': '20px'}),
                        html.H3("¡Gracias por usar la aplicación!", style={'fontWeight': 'normal'}),
                        html.H4("Propiedad de EDAI TU", style={'fontWeight': 'normal'})
                    ], style={'textAlign': 'center'})
                ], style={'position': 'fixed', 'top': 0, 'left': 0, 'width': '100vw', 'height': '100vh', 'backgroundColor': 'black',
                          'color': 'white', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center',
                          'flexDirection': 'column', 'fontSize': '2em', 'zIndex': 9999})
            return None


    if not _output_exists('mensaje-cierre', 'children'):
        @app.callback(Output('mensaje-cierre', 'children'), Input('boton-cerrar-app', 'n_clicks'), prevent_initial_call=True)
        def cerrar_aplicacion(n_clicks):
            if n_clicks:
                def cerrar():
                    time.sleep(1.5)
                    os._exit(0)
                threading.Thread(target=cerrar, daemon=True).start()
                return 'La aplicación se cerrará en un momento...'
            return ''

    setattr(app, "_callbacks_control_registered", True)


