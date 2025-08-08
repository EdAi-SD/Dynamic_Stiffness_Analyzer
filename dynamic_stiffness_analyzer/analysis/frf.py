from __future__ import annotations

import numpy as np


def calculate_H1(S_ff: np.ndarray, S_xf: np.ndarray) -> np.ndarray:
    return S_xf / (S_ff + 1e-12)


def calculate_H2(S_xx: np.ndarray, S_xf: np.ndarray) -> np.ndarray:
    return S_xx / (np.conj(S_xf) + 1e-12)


def calculate_coherence(S_ff: np.ndarray, S_xx: np.ndarray, S_xf: np.ndarray) -> np.ndarray:
    return np.abs(S_xf) ** 2 / (S_ff * S_xx + 1e-12)


def calculate_Hv(S_ff: np.ndarray, S_xx: np.ndarray, S_xf: np.ndarray) -> np.ndarray:
    H1 = calculate_H1(S_ff, S_xf)
    H2 = calculate_H2(S_xx, S_xf)
    coh = calculate_coherence(S_ff, S_xx, S_xf)
    # Optimización: umbrales menos restrictivos para coherencia
    return np.where(coh > 0.8, H1, np.where(coh > 0.5, np.sqrt(H1 * H2), H2))


