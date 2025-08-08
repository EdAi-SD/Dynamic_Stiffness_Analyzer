from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy.signal import butter, medfilt, sosfiltfilt

from dynamic_stiffness_analyzer.config.settings import CONFIG


def _filtro_multibanda_adaptativo(
    y_original: np.ndarray,
    fs: float,
    frecuencias_centrales: Sequence[float],
    ancho_banda: float = 20.0,
    perdida_max: float = 0.10,
    max_iter: int = 5,
) -> Tuple[np.ndarray, str]:
    if not frecuencias_centrales:
        return y_original, "Sin frecuencias centrales para filtro multibanda"
    y_filtrado = y_original.copy()
    mensaje_debug: List[str] = []
    for fc in frecuencias_centrales:
        try:
            if fc <= 0 or fc >= fs / 2:
                mensaje_debug.append(
                    f"Frecuencia {fc:.1f} Hz fuera del rango válido (0-{fs / 2:.1f} Hz)"
                )
                continue
            ancho_actual = ancho_banda
            mejor_resultado = None
            for _ in range(max_iter):
                f_low = max(CONFIG.LIMITES_FISICOS['FREQ_MIN'], fc - ancho_actual / 2)
                f_high = min(fs / 2 - CONFIG.LIMITES_FISICOS['FREQ_MIN'], fc + ancho_actual / 2)
                if f_low >= f_high:
                    break
                sos = butter(4, [f_low, f_high], btype='band', fs=fs, output='sos')
                y_temp = sosfiltfilt(sos, y_filtrado)
                energia_original = np.var(y_filtrado)
                energia_filtrada = np.var(y_temp)
                perdida = 1 - (energia_filtrada / max(energia_original, 1e-10))
                if perdida <= perdida_max:
                    mejor_resultado = y_temp
                    mensaje_debug.append(
                        f"FC {fc:.1f} Hz: BW={ancho_actual:.1f} Hz, pérdida={perdida:.2%}"
                    )
                    break
                else:
                    ancho_actual *= 1.2
            if mejor_resultado is not None:
                y_filtrado = mejor_resultado
            else:
                mensaje_debug.append(f"No se pudo optimizar filtro para {fc:.1f} Hz")
        except Exception as e:
            mensaje_debug.append(f"Error en filtro {fc:.1f} Hz: {str(e)[:30]}")
    return y_filtrado, "; ".join(mensaje_debug)


def filtrar_senal(
    df: pd.DataFrame,
    seleccion_multi: Sequence[str],
    seleccion_eje: str,
    fs: float,
    mediana_val: float | None,
    highpass_val: float | None,
    bandpass_multibanda: str | None,
    toggle_mediana: str,
    toggle_highpass: str,
    toggle_bandpass: str,
):
    mensajes_filtro: List[str] = []
    df_filtrado = df.copy()
    señales_a_filtrar = set(seleccion_multi or [])

    try:
        frecuencias_centrales = [
            float(f.strip()) for f in (bandpass_multibanda or '').split(',') if f.strip()
        ]
    except Exception:
        frecuencias_centrales = []

    for col in señales_a_filtrar:
        if col not in df_filtrado.columns:
            continue
        y_original = df_filtrado[col].values.copy()

        if toggle_mediana == 'yes' and mediana_val and mediana_val > 0:
            try:
                y_filtrado = medfilt(y_original, kernel_size=int(mediana_val))
                df_filtrado[col] = y_filtrado
                mensajes_filtro.append(f"Mediana aplicada a {col}: kernel={mediana_val}")
            except Exception as e:
                mensajes_filtro.append(f"Error mediana {col}: {str(e)[:30]}")

        if toggle_highpass == 'yes' and highpass_val and highpass_val > 0:
            try:
                if highpass_val < fs / 2:
                    sos = butter(4, highpass_val, btype='high', fs=fs, output='sos')
                    y_filtrado = sosfiltfilt(sos, df_filtrado[col].values)
                    df_filtrado[col] = y_filtrado
                    mensajes_filtro.append(f"Pasa-altos aplicado a {col}: fc={highpass_val} Hz")
            except Exception as e:
                mensajes_filtro.append(f"Error pasa-altos {col}: {str(e)[:30]}")

        if toggle_bandpass == 'yes' and frecuencias_centrales:
            try:
                y_filtrado, msg_debug = _filtro_multibanda_adaptativo(
                    df_filtrado[col].values, fs, frecuencias_centrales
                )
                df_filtrado[col] = y_filtrado
                mensajes_filtro.append(f"Multibanda {col}: {msg_debug}")
            except Exception as e:
                mensajes_filtro.append(f"Error multibanda {col}: {str(e)[:30]}")

    return df_filtrado, mensajes_filtro, True


