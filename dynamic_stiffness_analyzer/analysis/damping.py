from __future__ import annotations

import numpy as np
from typing import Dict, List, Optional
from scipy.fft import rfft, rfftfreq
from scipy.signal import find_peaks, get_window
from scipy.stats import median_abs_deviation


def calculo_amortiguamiento(accel: np.ndarray, fs: float, frecuencias_centrales: Optional[List[float]] = None, ventana_busqueda_hz: float = 5.0) -> Dict[str, object]:
    resultado = {'modos': [], 'zeta_global': None, 'mensajes': []}
    Nfft = len(accel)
    accel_fft = np.abs(rfft(accel * get_window('hann', Nfft)))
    freq_fft = rfftfreq(Nfft, 1 / fs)
    med_fft = np.median(accel_fft)
    mad_fft = median_abs_deviation(accel_fft)
    factor_ruido = 2
    height_fft = med_fft * factor_ruido
    prominence_fft = mad_fft * factor_ruido

    if frecuencias_centrales and len(frecuencias_centrales) > 0:
        frecuencias_centrales = np.sort(np.array(frecuencias_centrales, dtype=float))
        grupos = []
        grupo_actual = [frecuencias_centrales[0]]
        for f in frecuencias_centrales[1:]:
            if abs(f - grupo_actual[-1]) <= ventana_busqueda_hz:
                grupo_actual.append(f)
            else:
                grupos.append(grupo_actual)
                grupo_actual = [f]
        grupos.append(grupo_actual)
        picos_fft = []
        for grupo in grupos:
            f_min = min(grupo) - ventana_busqueda_hz / 2
            f_max = max(grupo) + ventana_busqueda_hz / 2
            idx_cerca = np.where((freq_fft >= f_min) & (freq_fft <= f_max))[0]
            if len(idx_cerca) == 0:
                continue
            sub_mag = accel_fft[idx_cerca]
            if len(sub_mag) == 0:
                continue
            pk, _ = find_peaks(sub_mag, height=height_fft, prominence=prominence_fft, distance=3)
            if len(pk) == 0:
                continue
            pk_max = pk[np.argmax(sub_mag[pk])]
            picos_fft.append(idx_cerca[pk_max])
        picos_fft = np.unique(picos_fft).astype(int)
    else:
        picos_fft, _ = find_peaks(accel_fft, height=height_fft, prominence=prominence_fft, distance=3)
        picos_fft = picos_fft.astype(int)

    for peak in picos_fft:
        peak_mag = accel_fft[peak]
        half_power = peak_mag / np.sqrt(2)
        left = peak
        while left > 0 and accel_fft[left] > half_power:
            left -= 1
        right = peak
        while right < len(accel_fft) - 1 and accel_fft[right] > half_power:
            right += 1
        if left == 0 or right == len(accel_fft) - 1:
            resultado['mensajes'].append(f"No se pudo estimar el ancho de banda para el modo en {freq_fft[peak]:.2f} Hz.")
            continue
        f1 = freq_fft[left]
        f2 = freq_fft[right]
        fn = freq_fft[peak]
        zeta = (f2 - f1) / (2 * fn)
        if 0 < zeta < 0.5:
            resultado['modos'].append({'frecuencia': fn, 'zeta': zeta, 'f1': f1, 'f2': f2, 'tipo': 'modal'})
        else:
            resultado['mensajes'].append(f"Amortiguamiento no físico o fuera de rango para el modo en {fn:.2f} Hz: zeta={zeta:.4f}")

    def damping_least_squares(signal: np.ndarray, fs: float):
        prominence = 0.05 * (np.max(signal) - np.min(signal))
        peaks, _ = find_peaks(signal, prominence=prominence)
        if len(peaks) < 2:
            return None
        t_peaks = np.array(peaks) / fs
        vals = np.abs(signal[peaks])
        N = min(8, len(vals))
        if N < 2:
            return None
        t_peaks = t_peaks[:N]
        vals = vals[:N]
        lnA = np.log(vals)
        periods = np.diff(t_peaks)
        if np.any(periods <= 0):
            return None
        freq = 1 / np.mean(periods)
        w = 2 * np.pi * freq
        A = np.vstack([t_peaks, np.ones_like(t_peaks)]).T
        result = np.linalg.lstsq(A, lnA, rcond=None)
        slope = result[0][0]
        zeta = -slope / w
        if zeta < 0 or zeta > 1:
            return None
        return zeta

    zeta_global = damping_least_squares(accel, fs)
    resultado['zeta_global'] = zeta_global
    if zeta_global is None:
        resultado['mensajes'].append(
            "No se pudo calcular el amortiguamiento global: no se detectaron picos suficientemente prominentes en la señal en el tiempo."
        )
    resultado['zeta_fisico'] = None
    return resultado



