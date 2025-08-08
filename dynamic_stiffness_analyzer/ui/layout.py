from __future__ import annotations

"""
Layout provisional: devuelve el layout existente del módulo original.
En una fase posterior copiaremos el árbol y lo haremos UI-agnóstico.
"""

import importlib.util
from pathlib import Path
from typing import Any


def _resolve_legacy_path() -> Path:
    # Intenta varias ubicaciones posibles del archivo original
    candidates = [
        Path(__file__).parents[2] / "Programa_finaal(RD_V10.4).py",          # raíz del repo
        Path(__file__).parents[1] / "Programa_finaal(RD_V10.4).py",          # paquete (por si acaso)
        Path.cwd() / "Programa_finaal(RD_V10.4).py",                          # cwd
    ]
    for c in candidates:
        if c.exists():
            return c
    # Devuelve la primera por consistencia; fallará y se manejará arriba
    return candidates[0]


def _load_legacy_module():
    legacy_path = _resolve_legacy_path()
    spec = importlib.util.spec_from_file_location("legacy_app", str(legacy_path))
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def build_layout(*_args: Any, **_kwargs: Any):
    legacy = _load_legacy_module()
    return legacy.app.layout


