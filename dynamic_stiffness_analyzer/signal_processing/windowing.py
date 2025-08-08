from __future__ import annotations

import numpy as np
from scipy.signal import periodogram

from dynamic_stiffness_analyzer.config.settings import CONFIG


def estimate_adaptive_tau(signal: np.ndarray, fs: float, damping_estimate: float = 0.02) -> float:
    envelope = np.abs(signal)
    max_amp = np.max(envelope)
    decay_threshold = CONFIG.TOLERANCIAS['DECAY_THRESHOLD'] * max_amp
    decay_indices = np.where(envelope < decay_threshold)[0]
    if len(decay_indices) > 0:
        decay_time_samples = decay_indices[0]
        decay_time_sec = decay_time_samples / fs
        tau_exp = decay_time_sec / 3
    else:
        def estimate_dominant_frequency(sig: np.ndarray, fs_local: float) -> float:
            f, Pxx = periodogram(sig, fs=fs_local)
            idx = np.argmax(Pxx)
            return f[idx] if len(f) > 0 else 1.0

        estimated_freq = estimate_dominant_frequency(signal, fs)
        if estimated_freq > 0:
            tau_exp = 1 / (2 * np.pi * estimated_freq * damping_estimate)
        else:
            T_record = len(signal) / fs
            if T_record > 5.0:
                tau_exp = T_record / 3
            elif T_record > 1.0:
                tau_exp = T_record / 4
            else:
                tau_exp = T_record / 5

    tau_exp = min(tau_exp, len(signal) / (3 * fs))
    return max(tau_exp, 0.01)


def ventana_exponencial(y: np.ndarray, fs: float, tau: float | None = None) -> np.ndarray:
    N = len(y)
    t = np.arange(N) / fs
    dur = N / fs
    if dur < 2.0 or N < 5000:
        tau_ = max(dur * 0.5, 0.5)
    else:
        if tau is None:
            tau_ = estimate_adaptive_tau(y, fs)
        else:
            tau_ = tau
        tau_ = max(tau_, dur * 0.7)
    ventana = np.exp(-t / tau_)
    return y * ventana


def ventana_fuerza_adaptativa(y: np.ndarray, fs: float) -> np.ndarray:
    y_abs = np.abs(y)
    if np.max(y_abs) == 0:
        return y
    force_norm = y_abs / np.max(y_abs)
    threshold_factor = CONFIG.TOLERANCIAS['THRESHOLD_FACTOR']
    indices = np.where(force_norm > threshold_factor)[0]
    if len(indices) == 0:
        impact_samples = int(0.005 * fs)
        start = 0
    else:
        start = indices[0]
        end = indices[-1]
        impact_samples = end - start + 1

    safety_margin = int(0.2 * impact_samples)
    total_window_samples = impact_samples + safety_margin
    min_samples = int(CONFIG.TOLERANCIAS['MIN_VENTANA_IMPACTO'] * fs)
    max_samples = int(CONFIG.TOLERANCIAS['MAX_VENTANA_IMPACTO'] * fs)
    total_window_samples = int(np.clip(total_window_samples, min_samples, max_samples))

    window = np.zeros(len(y))
    end_win = min(start + total_window_samples, len(y))
    window[start:end_win] = 1.0

    taper_samples = max(int(0.15 * total_window_samples), int(0.001 * fs))
    for i in range(taper_samples):
        idx = end_win - taper_samples + i
        if 0 <= idx < len(window):
            window[idx] *= 0.5 * (1 + np.cos(np.pi * i / taper_samples))
    return y * window


