# Dynamic Stiffness Analyzer — Refactor (Progreso)

Este documento describe la arquitectura, el plan de refactorización y los módulos/funciones creados hasta ahora, con sus entradas/salidas. Se actualizará a medida que avancemos.

## Estructura de carpetas (actual)

```
Dynamic_Stiffness_Analyzer/
  Programa_finaal(RD_V10.4).py        # Punto de entrada actual (Dash)
  README.md                            # README general del repo
  dynamic_stiffness_analyzer/
    __init__.py
    docs/
      README.md                        # Este documento
    config/
      settings.py                      # Configuración centralizada (CONFIG, USAR_CACHE)
    services/
      cache.py                         # Caché computacional LRU (CACHE)
    io/
      __init__.py
      loader.py                        # Carga de archivos (CSV/XLSX/TXT Catman)
      export.py                        # Exportación Waterfall a ZIP
    signal_processing/
      __init__.py
      windowing.py                     # Ventanas: exponencial y fuerza adaptativa
      filters.py                       # Filtros: mediana, pasa‑altos, multibanda adaptativo
      cutting.py                       # Corte temporal de señal con mínimos de puntos
    analysis/
      __init__.py
      frf.py                           # Estimadores H1/H2/Hv y coherencia
      dynamic_stiffness.py             # Rigidez dinámica robusta y antiresonancias
      damping.py                       # Amortiguamiento modal/global
    visualization/
      __init__.py
      time_plot.py                     # Gráfico de tiempo optimizado
      fft_plot.py                      # Gráfico FFT optimizado
      waterfall_plot.py                # Waterfall 3D adaptativo
      coherence_plot.py                # Gráfico de coherencia
      stiffness_plot.py                # Gráfico de rigidez dinámica (|K| y fase)
      shared.py                        # Figuras vacías, utilidades comunes
    ui/
      __init__.py                      # (placeholder) aquí irán layout y callbacks
```

## Plan de refactorización

- Fase 1 (hecho): Configuración y caché en módulos dedicados.
- Fase 2 (hecho): I/O (carga y exportación) y procesamiento base (ventaneo, filtros, corte).
- Fase 3 (pendiente): Análisis espectral/FRF/rigidez/coherencia → `analysis/`.
- Fase 4 (pendiente): Visualización → `visualization/` y callbacks delgados en `ui/`.
- Fase 5 (pendiente): Tests, linters/format y limpieza final.

## Archivos y funcionalidades (propósito, entradas, salidas)

### dynamic_stiffness_analyzer/config/settings.py
- Propósito: Centralizar parámetros y límites del sistema.
- Símbolos:
  - `class ConfiguracionSistema`: agrupa diccionarios `VISUALIZACION`, `VENTANAS_WATERFALL`, `UMBRALES_DATOS`, `LIMITES_FISICOS`, `TOLERANCIAS`.
  - `CONFIG`: instancia global de `ConfiguracionSistema`.
  - `USAR_CACHE: bool`: bandera global para uso de caché.
- Entradas: —
- Salidas: objetos/constantes de configuración.

### dynamic_stiffness_analyzer/services/cache.py
- Propósito: Proveer un caché LRU simple para resultados costosos.
- Símbolos:
  - `@dataclass CacheComputacional(max_cache_size=50)`
    - `generar_hash_parametros(*args, **kwargs) -> Optional[str]`
    - `obtener_de_cache(cache_key) -> Optional[Any]`
    - `guardar_en_cache(cache_key, resultado) -> None`
    - `limpiar_cache() -> None`
    - `estadisticas_cache() -> Dict[str, Any]`
  - `CACHE = CacheComputacional()`
- Entradas: claves de caché, resultados.
- Salidas: resultados en caché, estadísticas.

### dynamic_stiffness_analyzer/io/loader.py
- Propósito: Cargar contenidos subidos desde la UI (dcc.Upload) con autodetección de formato.
- Funciones:
  - `_detectar_separador(linea: str) -> str`
  - `_mapear_columnas_flex(df: pd.DataFrame, columnas_esperadas: List[str]) -> Optional[pd.DataFrame]`
  - `cargar_contenidos_upload(contents: str, filename: str) -> Tuple[str, Optional[str], str]`
    - Entradas: `contents` (cadena base64 de dcc.Upload), `filename`.
    - Salidas: `(mensaje_ui, df_json_or_None, mensaje_cargando)`; `df_json` en `orient='split'`.
    - Soporta `.csv`, `.xlsx` y TXT Catman; renombra columnas por nombre o posición.

### dynamic_stiffness_analyzer/io/export.py
- Propósito: Exportar los datos del Waterfall a ZIP con dos CSV (largo y matriz).
- Funciones:
  - `exportar_waterfall_a_zip(datos: Iterable[dict]) -> Optional[str]`
    - Entradas: iterable de dicts con `segmento`, `tiempo_central`, `frecuencia`, `amplitud`.
    - Salidas: ruta a fichero ZIP temporal (o `None`).

### dynamic_stiffness_analyzer/signal_processing/windowing.py
- Propósito: Ventaneo adaptativo para análisis transitorio.
- Funciones:
  - `estimate_adaptive_tau(signal: np.ndarray, fs: float, damping_estimate: float = 0.02) -> float`
  - `ventana_exponencial(y: np.ndarray, fs: float, tau: float | None = None) -> np.ndarray`
  - `ventana_fuerza_adaptativa(y: np.ndarray, fs: float) -> np.ndarray`
- Entradas: arrays de señal y `fs` (Hz).
- Salidas: señal ventaneada o `tau` estimado.

### dynamic_stiffness_analyzer/signal_processing/filters.py
- Propósito: Aplicar filtros a las señales seleccionadas.
- Funciones:
  - `filtrar_senal(df: pd.DataFrame, seleccion_multi: Sequence[str], seleccion_eje: str, fs: float, mediana_val: float | None, highpass_val: float | None, bandpass_multibanda: str | None, toggle_mediana: str, toggle_highpass: str, toggle_bandpass: str) -> Tuple[pd.DataFrame, List[str], bool]`
  - `*_filtro_multibanda_adaptativo(...): Tuple[np.ndarray, str]`
- Entradas: DataFrame estándar y parámetros/toggles.
- Salidas: `df_filtrado`, lista de mensajes y bandera de éxito.

### dynamic_stiffness_analyzer/signal_processing/cutting.py
- Propósito: Corte temporal garantizando mínimos de puntos para FFT/Waterfall/Welch.
- Funciones:
  - `aplicar_corte_df(df: pd.DataFrame, inicio: float, fin: float, señales_seleccionadas: Optional[Sequence[str]] = None) -> Tuple[pd.DataFrame, str]`
- Entradas: DataFrame estándar y rango temporal.
- Salidas: DataFrame cortado y mensaje descriptivo.

### Programa_finaal(RD_V10.4).py (punto de entrada actual)
- UI y callbacks de Dash; ahora delega en módulos:
  - Carga: `io.loader.cargar_contenidos_upload`.
  - Exportación: `io.export.exportar_waterfall_a_zip`.
  - Filtros: `signal_processing.filters.filtrar_senal`.
  - Ventanas: `signal_processing.windowing.*`.
  - Corte: `signal_processing.cutting.aplicar_corte_df`.

## Próximos módulos (planificados)

- `analysis/frf.py`: estimadores H1/H2/Hv, coherencia.
- `analysis/dynamic_stiffness.py`: rigidez dinámica y antiresonancias.
- `analysis/damping.py`: cálculo de amortiguamiento.
- `visualization/*`: gráficos tiempo/FFT/waterfall/coherencia/rigidez y utilidades comunes.
- `ui/*`: layout y callbacks particionados por dominio.

## Notas de diseño

- La UI orquesta; la lógica científica se encapsula en funciones puras (facilita tests y futura GUI PyQtGraph).
- Configuración tipada y centralizada; sin “números mágicos” embebidos en algoritmos.
- Caché LRU desacoplado para acelerar cálculos repetitivos en datasets grandes.
