from __future__ import annotations


class ConfiguracionSistema:
    """
    Configuración centralizada de parámetros del sistema.
    Mantiene límites de visualización, tamaños de ventana, umbrales de datos,
    límites físicos y tolerancias numéricas.
    """

    # Límites de visualización
    VISUALIZACION = {
        "MAX_PUNTOS_TIEMPO": 20000,      # Reducir puntos para gráfico tiempo si excede
        "MAX_PUNTOS_FFT": 50000,         # Reducir puntos para gráfico FFT si excede
        "REDUCCION_VISUAL_FFT": 20000,   # Objetivo de puntos tras reducción
        "MAX_SEGMENTOS_WATERFALL": 120,  # Máximo segmentos en waterfall 3D
    }

    # Tamaños de ventana para waterfall
    VENTANAS_WATERFALL = {
        "GRANDE": 4096,    # Para datasets > 100k puntos
        "MEDIO": 2048,     # Para datasets > 50k puntos
        "PEQUEÑO": 1024,   # Para datasets normales
        "MINIMO": 512,     # Ventana mínima absoluta
    }

    # Umbrales de datos
    UMBRALES_DATOS = {
        "DATASET_GRANDE": 100000,     # Puntos para considerar dataset grande
        "DATASET_MEDIO": 50000,       # Puntos para considerar dataset medio
        "MIN_SEGMENTOS_WELCH": 6,     # Mínimo segmentos para análisis Welch
        "MIN_PUNTOS_SEGMENTO": 256,   # Mínimo puntos por segmento
        "MAX_PUNTOS_SEGMENTO": 1024,  # Máximo puntos por segmento
        "MAX_SEGMENTOS": 120,         # Máximo segmentos waterfall para rendimiento
        "MIN_AMPLITUD_RUIDO": 1e-8,   # Amplitud mínima considerada señal
        "FACTOR_UMBRAL_SFF": 0.01,    # 1% del máximo para Sff
    }

    # Validación física
    LIMITES_FISICOS = {
        "MASA_MIN": 0.1,       # kg - Masa mínima martillo
        "MASA_MAX": 50.0,      # kg - Masa máxima martillo
        "FREQ_MIN": 0.1,       # Hz - Frecuencia mínima válida
        "DT_MIN": 1e-6,        # s - dt mínimo válido
        "DT_MAX": 1.0,         # s - dt máximo válido
    }

    # Tolerancias numéricas
    TOLERANCIAS = {
        "IRREGULARIDAD_TEMPORAL": 0.05,   # 5% - Umbral para regenerar tiempo
        "EPSILON_DIVISION": 1e-12,        # Evitar división por cero
        "MIN_COHERENCIA_VALIDA": 1e-10,   # Coherencia mínima considerada válida
        "MIN_DURACION_SEGMENTO": 0.05,    # 50ms - Duración mínima de segmento
        "DECAY_THRESHOLD": 0.05,          # 5% amplitud - Umbral decaimiento señal
        "THRESHOLD_FACTOR": 0.1,          # 10% - Factor umbral ventana impacto
        "MAX_VENTANA_IMPACTO": 0.05,      # 50ms - Ventana máxima impacto
        "MIN_VENTANA_IMPACTO": 0.0005,    # 0.5ms - Ventana mínima impacto
        "MARGEN_GRAFICO": 0.05,           # 5% margen extra en ejes Y
    }


# Instancia global de configuración
CONFIG = ConfiguracionSistema()


# Flag global para activar/desactivar caché a nivel de aplicación
USAR_CACHE: bool = False


