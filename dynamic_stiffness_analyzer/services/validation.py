from __future__ import annotations

from typing import Tuple

try:
    # Usar configuración centralizada si está disponible
    from dynamic_stiffness_analyzer.config.settings import CONFIG
except Exception:  # fallback mínimo si no carga la config externa
    class _ConfigFallback:
        LIMITES_FISICOS = {
            'MASA_MIN': 0.1,
            'MASA_MAX': 50.0,
        }

    CONFIG = _ConfigFallback()  # type: ignore


def validar_masa_martillo(masa: float | None) -> Tuple[float, str]:
    """Valida la masa del martillo y devuelve (masa_validada, mensaje).

    - Si es None o fuera de rango físico, se ajusta al límite válido y se informa.
    """
    if masa is None:
        return 1.0, "Masa no especificada, usando 1.0 kg por defecto"
    if masa <= 0:
        return 1.0, "Masa debe ser positiva, usando 1.0 kg por defecto"
    if masa < CONFIG.LIMITES_FISICOS['MASA_MIN']:
        return (
            CONFIG.LIMITES_FISICOS['MASA_MIN'],
            f"Masa muy pequeña ({masa} kg), ajustada a {CONFIG.LIMITES_FISICOS['MASA_MIN']} kg",
        )
    if masa > CONFIG.LIMITES_FISICOS['MASA_MAX']:
        return (
            CONFIG.LIMITES_FISICOS['MASA_MAX'],
            f"Masa muy grande ({masa} kg), ajustada a {CONFIG.LIMITES_FISICOS['MASA_MAX']} kg",
        )
    return masa, f"Masa del martillo: {masa} kg"


