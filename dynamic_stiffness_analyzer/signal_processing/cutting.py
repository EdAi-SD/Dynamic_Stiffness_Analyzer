from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from dynamic_stiffness_analyzer.config.settings import CONFIG


def aplicar_corte_df(
    df: pd.DataFrame,
    inicio: float,
    fin: float,
    señales_seleccionadas: Optional[Sequence[str]] = None,
) -> Tuple[pd.DataFrame, str]:
    """
    Aplica un corte temporal a `df` asegurando un mínimo de puntos para FFT/Waterfall/Welch.

    Entradas:
    - df: DataFrame con columnas estándar ('tiempo', 'fuerza', 'accel_x', 'accel_y', 'accel_z').
    - inicio, fin: tiempos en segundos.
    - señales_seleccionadas: columnas adicionales a incluir si existen.

    Salidas:
    - (df_corte, mensaje)
    """
    if df is None or df.empty or 'tiempo' not in df.columns:
        raise ValueError("Datos inválidos para corte")
    if inicio is None or fin is None or inicio >= fin:
        raise ValueError("Rango de corte inválido")

    if not señales_seleccionadas:
        señales_seleccionadas = ['accel_x']

    # Mínimos de puntos (alineados con la lógica original)
    min_fft = 4096
    min_segmentos = CONFIG.UMBRALES_DATOS.get('MIN_SEGMENTOS_WELCH', 6)
    window_min = CONFIG.UMBRALES_DATOS.get('MIN_PUNTOS_SEGMENTO', 256)
    min_waterfall = min_segmentos * window_min
    nperseg_welch = CONFIG.UMBRALES_DATOS.get('MAX_PUNTOS_SEGMENTO', 1024)
    min_segments_welch = CONFIG.UMBRALES_DATOS.get('MIN_SEGMENTOS_WELCH', 6)
    min_welch = nperseg_welch + (min_segments_welch - 1) * int(nperseg_welch * 0.5)
    min_puntos = max(min_fft, min_waterfall, min_welch)

    t_min = df['tiempo'].min()
    t_max = df['tiempo'].max()
    paso = df['tiempo'].iloc[1] - df['tiempo'].iloc[0] if len(df) > 1 else 0.01
    ampliado = False
    inicio_solicitado, fin_solicitado = inicio, fin
    mask = (df['tiempo'] >= inicio) & (df['tiempo'] <= fin)

    # 1. Ampliar solo el fin hacia adelante
    fin_temp = fin
    while mask.sum() < min_puntos and fin_temp < t_max:
        ampliado = True
        fin_temp = min(fin_temp + paso, t_max)
        mask = (df['tiempo'] >= inicio) & (df['tiempo'] <= fin_temp)

    # 2. Si aún no hay suficientes puntos, ampliar el inicio hacia atrás
    inicio_temp = inicio
    while mask.sum() < min_puntos and inicio_temp > t_min:
        ampliado = True
        inicio_temp = max(inicio_temp - paso, t_min)
        mask = (df['tiempo'] >= inicio_temp) & (df['tiempo'] <= fin_temp)

    # Usar los valores ampliados
    inicio, fin = inicio_temp, fin_temp
    columnas_clave = ['tiempo', 'fuerza', 'accel_x', 'accel_y', 'accel_z']
    columnas_corte = list(dict.fromkeys(columnas_clave + [col for col in señales_seleccionadas if col in df.columns]))
    columnas_corte = [col for col in columnas_corte if col in df.columns]
    df_corte = df.loc[(df['tiempo'] >= inicio) & (df['tiempo'] <= fin), columnas_corte].copy()
    if df_corte[columnas_corte].dropna(how='all').empty:
        raise ValueError('No hay datos en el rango seleccionado')

    if ampliado:
        mensaje = (
            f'Corte solicitado: {inicio_solicitado:.2f} s a {fin_solicitado:.2f} s. '
            f'Corte aplicado: {inicio:.2f} s a {fin:.2f} s, {df_corte.shape[0]} puntos. '
            '(El rango fue ampliado automáticamente para asegurar el mínimo de puntos necesarios.)'
        )
    else:
        mensaje = f'Corte aplicado: {inicio:.2f} s a {fin:.2f} s, {df_corte.shape[0]} puntos.'

    return df_corte, mensaje


