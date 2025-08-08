from __future__ import annotations

from dash import Output, Input, dcc
import sys
import importlib

from app_legacy import app
from dynamic_stiffness_analyzer.io.export import exportar_waterfall_a_zip


@app.callback(Output('descarga-waterfall', 'data'), Input('boton-exportar-waterfall', 'n_clicks'), prevent_initial_call=True)
def exportar_waterfall(n_clicks):
    # Importar el módulo legado ya cargado dinámicamente y tomar el atributo generado
    legacy_mod = sys.modules.get('legacy_app')
    if legacy_mod is None:
        try:
            legacy_mod = importlib.import_module('legacy_app')
        except Exception:
            legacy_mod = None

    datos = None
    if legacy_mod and hasattr(legacy_mod, 'actualizar_graficos'):
        datos = getattr(legacy_mod.actualizar_graficos, 'datos_waterfall', None)

    if not datos:
        return None
    zip_path = exportar_waterfall_a_zip(datos)
    if not zip_path:
        return None
    return dcc.send_file(zip_path, filename="datos_3D.zip")


