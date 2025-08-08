from __future__ import annotations

import webbrowser
from app_legacy import app  # carga el módulo legado y expone `app`

# Registrar callbacks migrados para que queden activos en la instancia de `app`
# Importar módulos que registran callbacks por efectos secundarios de import
try:
    # Control de cierre y overlay
    import dynamic_stiffness_analyzer.ui.callbacks.control  # noqa: F401
    # Exportación de waterfall
    import dynamic_stiffness_analyzer.ui.callbacks.export  # noqa: F401
except Exception as e:
    # No bloquear el arranque si aún no existen
    print(f"[UI] Aviso: callbacks modulares no cargados: {e}")


if __name__ == "__main__":
    webbrowser.open_new("http://127.0.0.1:8050")
    app.run(debug=False, use_reloader=False)


