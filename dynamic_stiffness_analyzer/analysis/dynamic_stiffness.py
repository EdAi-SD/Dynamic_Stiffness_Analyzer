from __future__ import annotations

import numpy as np

from .frf import calculate_coherence


def detect_antiresonances(H_frf: np.ndarray, frequencies: np.ndarray, fK: np.ndarray, S_ff: np.ndarray, S_xx: np.ndarray, S_xf: np.ndarray, window_hz: float = 10) -> np.ndarray:
    try:
        H_magnitude_db = 20 * np.log10(np.abs(H_frf) + 1e-12)
        # Piso de ruido local fuera de picos prominentes
        # Aproximación simple sin dependencia de find_peaks (evitar import pesado aquí)
        noise_floor = np.median(H_magnitude_db)
        threshold_db = max(-35, noise_floor + 10)
        antires_mask = H_magnitude_db < threshold_db
        # Filtrar por coherencia
        coh = calculate_coherence(S_ff, S_xx, S_xf)
        coh_interp = np.interp(frequencies, fK, coh) if len(fK) == len(coh) else coh
        antires_mask = antires_mask & (coh_interp > 0.6)
        return antires_mask
    except Exception:
        return np.zeros_like(frequencies, dtype=bool)


def calculate_dynamic_stiffness_robust(H_frf: np.ndarray, frequencies: np.ndarray, fK: np.ndarray, S_ff: np.ndarray, S_xx: np.ndarray, S_xf: np.ndarray) -> np.ndarray:
    try:
        antires_mask = detect_antiresonances(H_frf, frequencies, fK, S_ff, S_xx, S_xf)
        valid_mask = ~antires_mask & (np.abs(H_frf) > 1e-10)
        omega = 2 * np.pi * frequencies[valid_mask]
        H_valid = H_frf[valid_mask]
        K_dynamic = np.zeros_like(H_frf, dtype=complex)
        if len(H_valid) > 0:
            K_dynamic[valid_mask] = -omega ** 2 / H_valid
        if np.any(antires_mask) and np.any(valid_mask):
            K_dynamic_real_interp = np.interp(frequencies[antires_mask], frequencies[valid_mask], np.real(K_dynamic[valid_mask]))
            K_dynamic_imag_interp = np.interp(frequencies[antires_mask], frequencies[valid_mask], np.imag(K_dynamic[valid_mask]))
            K_dynamic[antires_mask] = K_dynamic_real_interp + 1j * K_dynamic_imag_interp
        return K_dynamic
    except Exception:
        return np.zeros_like(H_frf, dtype=complex)



