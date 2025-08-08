from __future__ import annotations

"""
Puente temporal: expone `app` del archivo original mientras finalizamos la migración.
"""

import importlib.util
from pathlib import Path


def _resolve_legacy_path() -> Path:
    candidates = [
        Path(__file__).parent / "Programa_finaal(RD_V10.4).py",
        Path.cwd() / "Programa_finaal(RD_V10.4).py",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]


def _load_original():
    legacy_path = _resolve_legacy_path()
    spec = importlib.util.spec_from_file_location("legacy_app", str(legacy_path))
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


_mod = _load_original()
app = _mod.app  # reexport

# NOTA: No reasignamos layout ni recargamos callbacks del módulo original aquí.
# Si se intenta cargar el módulo otra vez, se crearían callbacks en una instancia
# distinta de Dash y los eventos (como la carga de CSV) no dispararían.


