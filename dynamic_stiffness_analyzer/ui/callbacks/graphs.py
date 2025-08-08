from __future__ import annotations

"""
Registro provisional de callbacks: reexporta los callbacks desde el módulo original
para mantener la funcionalidad mientras terminamos la migración.
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
    # En esta fase los callbacks ya están declarados en el módulo original al importarse.
    # Aquí solo aseguramos que el módulo se cargue (lo cual registra los decorators).
    _load_legacy_module()
    return app


