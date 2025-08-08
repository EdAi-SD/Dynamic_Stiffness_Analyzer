from __future__ import annotations

"""
Registro de callbacks principales de gráficos.
Mientras migramos, seguimos cargando el módulo legado para el callback
"actualizar_graficos" y otros que aún no se han extraído.
"""

import importlib.util
from pathlib import Path


def _resolve_legacy_path() -> Path:
    candidates = [
        Path(__file__).parents[2] / "Programa_finaal(RD_V10.4).py",
        Path(__file__).parents[1] / "Programa_finaal(RD_V10.4).py",
        Path.cwd() / "Programa_finaal(RD_V10.4).py",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]


def _load_legacy_module():
    legacy_path = _resolve_legacy_path()
    spec = importlib.util.spec_from_file_location("legacy_app", str(legacy_path))
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def register_callbacks(app):
    # Cargar callbacks del módulo legado (actualizar_graficos y otros aún no migrados)
    _load_legacy_module()
    # Importar módulos que registran callbacks extraídos (control, export, filtros, corte, masa)
    # La importación se hace aquí para asegurar que exista una única instancia de app y evitar duplicados.
    from . import control  # noqa: F401
    from . import export  # noqa: F401
    from . import filters  # noqa: F401
    from . import cutting  # noqa: F401
    from . import mass  # noqa: F401
    return app


