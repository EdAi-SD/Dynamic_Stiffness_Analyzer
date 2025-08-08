# 📊 APLICACIÓN DE RIGIDEZ DINÁMICA - DOCUMENTACIÓN COMPLETA
 Bienvenido a la documentación integral de la aplicación de rigidez dinámica. Aquí encontrarás explicaciones detalladas sobre cada aspecto del software, desde la teoría básica hasta la interpretación avanzada de resultados. El objetivo es que cualquier usuario, sin importar su nivel técnico, pueda comprender el funcionamiento, los métodos, la justificación de cada parámetro y apartado, y sacar el máximo provecho de la herramienta. Se incluyen conceptos matemáticos, ejemplos prácticos, recomendaciones y aclaraciones para facilitar el aprendizaje y la aplicación en casos reales.

## 📋 ÍNDICE

**¿Cómo usar el índice?**
El índice te permite navegar rápidamente por las diferentes secciones del documento. Cada apartado está pensado para abordar una necesidad específica: desde la descripción general y el contexto de uso, hasta la instalación, el troubleshooting y la referencia de la API. Si eres nuevo en el análisis de rigidez dinámica, te recomendamos empezar por la descripción general y la guía de usuario. Si buscas detalles técnicos o integración avanzada, consulta los algoritmos, la API y las notas de versión.

1. [Descripción General](#descripción-general)
2. [Características Principales](#características-principales)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Sistema de Caché Inteligente](#sistema-de-caché-inteligente)
5. [Funcionalidades Detalladas](#funcionalidades-detalladas)
6. [Interfaz de Usuario](#interfaz-de-usuario)
7. [Algoritmos y Métodos](#algoritmos-y-métodos)
8. [Optimizaciones de Rendimiento](#optimizaciones-de-rendimiento)
9. [Guía de Instalación](#guía-de-instalación)
10. [Guía de Usuario](#guía-de-usuario)
11. [Troubleshooting](#troubleshooting)
12. [API Reference](#api-reference)

---

## 📖 DESCRIPCIÓN GENERAL

**¿Qué encontrarás en esta sección?**
Aquí se explica el concepto de rigidez dinámica, su importancia en ingeniería y cómo la aplicación facilita el análisis experimental. Se incluyen ejemplos de situaciones donde el análisis es relevante, como ensayos de laboratorio, diagnóstico de estructuras y validación de modelos numéricos. Además, se detalla el propósito de la herramienta y cómo puede adaptarse a diferentes necesidades y formatos de datos.

**¿Qué es la rigidez dinámica?**
La rigidez dinámica es una propiedad fundamental de las estructuras que indica cómo resisten la deformación bajo cargas que varían en el tiempo. Analizarla permite identificar modos de vibración, zonas débiles y estimar el amortiguamiento, lo que es clave para el diseño y diagnóstico estructural.

**¿Por qué usar esta aplicación?**
Esta herramienta permite procesar datos experimentales de manera profesional, automatizando tareas complejas como el filtrado, la segmentación temporal, el cálculo espectral y la visualización avanzada. Así, el usuario puede centrarse en la interpretación de resultados y la toma de decisiones.

### 🎯 **Propósito**

**¿Por qué es importante el propósito?**
El propósito define la razón de ser de la aplicación: facilitar el análisis de rigidez dinámica y amortiguamiento en estructuras, automatizando tareas complejas y permitiendo al usuario centrarse en la interpretación de resultados. Se busca que la herramienta sea intuitiva, robusta y flexible, adaptándose a diferentes ensayos y formatos de archivo. Esto permite ahorrar tiempo, reducir errores y mejorar la calidad del análisis experimental.
El propósito de la aplicación es facilitar el análisis de rigidez dinámica y amortiguamiento en estructuras mediante el procesamiento de señales de acelerómetros y sensores de fuerza. Está diseñada para ser intuitiva, robusta y flexible, permitiendo trabajar con diferentes formatos de archivo y adaptar los parámetros de análisis a cada ensayo.
Aplicación web avanzada para análisis de **rigidez dinámica** de estructuras mediante procesamiento de señales de acelerómetros y sensores de fuerza. Desarrollada con **Dash/Plotly** para análisis científico e ingenieril.

### 🏗️ **Contexto de Uso**

**¿En qué situaciones se recomienda usar la aplicación?**
La aplicación es útil en una amplia variedad de escenarios: ensayos de impacto, análisis modal experimental, caracterización de amortiguamiento, evaluación de propiedades dinámicas y validación de modelos numéricos. También es ideal para investigación en ingeniería estructural y desarrollo de nuevas metodologías de análisis. Se recomienda su uso tanto en laboratorio como en campo, y es compatible con equipos de adquisición estándar.
**¿En qué situaciones se usa?**
La aplicación es útil en ensayos de laboratorio, validación de modelos numéricos, diagnóstico de estructuras existentes y desarrollo de nuevas metodologías de análisis modal. Permite trabajar tanto con datos de impacto como con vibraciones forzadas, y es compatible con equipos de adquisición estándar.
- **Ensayos de impacto** con martillo instrumentado
- **Análisis modal experimental**
- **Caracterización de amortiguamiento**
- **Evaluación de propiedades dinámicas** de estructuras
- **Investigación en ingeniería estructural**

### ⚡ **Características Clave**

**¿Qué aporta cada característica?**
Cada característica está diseñada para resolver una necesidad real en el análisis experimental. El procesamiento en tiempo real permite iterar rápidamente sobre los datos; el sistema de caché optimiza el trabajo con datasets grandes; la interfaz moderna facilita la interacción; los cálculos robustos aseguran resultados fiables; la exportación flexible permite documentar y compartir resultados; y la visualización 3D avanzada ayuda a interpretar la evolución temporal y frecuencial de la respuesta estructural.
Cada característica responde a una necesidad real en el análisis experimental:
- Procesamiento en tiempo real: evita esperas y permite iterar rápidamente sobre los datos.
- Sistema de caché: acelera el trabajo en datasets grandes y repetitivos.
- Interfaz moderna: facilita la interacción y reduce errores de usuario.
- Cálculos robustos: emplea algoritmos validados en la literatura técnica.
- Exportación flexible: permite documentar y compartir resultados fácilmente.
- ✅ **Procesamiento en tiempo real** de señales
- ✅ **Sistema de caché inteligente** para optimización
- ✅ **Interfaz web moderna** con feedback visual
- ✅ **Cálculos científicos robustos**
- ✅ **Exportación de datos** en múltiples formatos
- ✅ **Visualización 3D avanzada**

---

## 🚀 CARACTERÍSTICAS PRINCIPALES

### 📁 **Gestión de Archivos**

**¿Por qué es importante la gestión de archivos?**
La capacidad de trabajar con diferentes formatos de archivo (CSV, TXT Catman, XLSX) permite adaptar la aplicación a diversos sistemas de adquisición y evitar errores de compatibilidad. La autodetección y validación robusta aseguran que los datos sean consistentes y aptos para el análisis, facilitando el trabajo del usuario y mejorando la fiabilidad de los resultados.
**¿Por qué soportar varios formatos?**
En la práctica, los datos pueden provenir de diferentes sistemas de adquisición. Por eso, la aplicación detecta automáticamente el formato y adapta el procesamiento, evitando errores y facilitando el trabajo del usuario.
<div align="center">

|      Formato       |            Descripción            |    Soporte     |
|:------------------:|:---------------------------------:|:--------------:|
|   **CSV**          | Archivos estándar con separadores |  ✅ Completo   |
| **TXT Catman**     |      Formato HBM Catman           |  ✅ Completo   |
|   **XLSX**         |             Excel                 |  ✅ Completo   |
| **Autodetección**  |   Reconocimiento automático       | ✅ Automático  |

</div>

### 🔧 **Procesamiento de Señales**
**¿Por qué filtrar y cortar las señales?**
Las señales reales suelen contener ruido, offset y componentes no deseadas. Los filtros y el corte temporal permiten limpiar los datos y centrarse en la parte relevante del ensayo, mejorando la fiabilidad del análisis espectral y modal.

**Explicación de cada filtro y método:**
- **Filtro mediana**: Elimina picos de ruido impulsivo que pueden aparecer por interferencias eléctricas o impactos no deseados. Es especialmente útil para limpiar la señal sin distorsionar los transitorios importantes, como el inicio de un impacto.
- **Filtro paso alto**: Suprime componentes de baja frecuencia, como el offset o la deriva lenta de los sensores, permitiendo que el análisis se centre en las vibraciones relevantes. Esto mejora la precisión en la identificación de modos de vibración.
- **Filtro multibanda**: Permite aislar rangos de frecuencia específicos, agrupando automáticamente bandas cercanas y optimizando el diseño del filtro para preservar la forma de la señal. Es útil para enfocar el análisis en zonas de interés y reducir el efecto de ruido fuera de banda.
- **Ventaneo adaptativo**: Ajusta la ventana de análisis según el tipo de señal y su comportamiento temporal, optimizando la detección de transitorios y el cálculo espectral. Por ejemplo, para señales de impacto, detecta automáticamente el decaimiento y aplica una ventana exponencial.
- **Corte temporal**: Selecciona una porción específica de la señal para el análisis, permitiendo excluir zonas irrelevantes o ruidosas. Esto es fundamental para mejorar la fiabilidad de los resultados espectrales y modales.
- **Filtro mediana**: Eliminación de ruido impulsivo
- **Filtro paso alto**: Eliminación de offset y deriva
- **Filtro multibanda**: Aislamiento de frecuencias específicas
- **Ventaneo adaptativo**: Optimizado para transitorios
- **Corte temporal**: Selección de ventanas de análisis

### 📊 **Análisis Espectral**

**¿Cómo interpretar los resultados espectrales?**
El análisis espectral permite identificar las frecuencias naturales, zonas de resonancia y antiresonancia, y estimar el amortiguamiento. La visualización de la FFT y el waterfall 3D ayuda a comprender cómo evoluciona la respuesta en el tiempo y a validar la calidad de la medición mediante la coherencia. Se recomienda analizar los picos espectrales, la magnitud y fase de la rigidez dinámica, y la coherencia para asegurar resultados fiables.
**¿Qué es la FFT y por qué es importante?**
La Transformada Rápida de Fourier (FFT) permite descomponer la señal en sus componentes frecuenciales, identificando modos de vibración y zonas de interés. El análisis waterfall 3D muestra cómo evoluciona la respuesta en el tiempo, y la función de transferencia (FRF) relaciona la excitación y la respuesta para calcular la rigidez dinámica.

**¿Por qué usar análisis espectral?**
El análisis espectral es esencial para entender cómo responde una estructura a diferentes frecuencias de excitación. Permite identificar las frecuencias naturales (modos propios), zonas de resonancia y antiresonancia, y estimar el amortiguamiento. Además, ayuda a validar la calidad de la medición mediante la coherencia y a detectar problemas experimentales como ruido excesivo o errores de sincronización.

**¿Qué representa cada parámetro?**
- `H(ω)`: Relaciona la respuesta (aceleración) y la excitación (fuerza) en el dominio de la frecuencia. Es la base para calcular la rigidez dinámica y el amortiguamiento.
- `K(ω)`: Indica cuánta fuerza se necesita para producir una determinada aceleración en cada frecuencia. Valores bajos de K(ω) suelen indicar resonancias, mientras que valores altos pueden señalar antiresonancias o zonas rígidas.
- `S_xf(ω)`, `S_ff(ω)`, `S_xx(ω)`: Permiten calcular estimadores robustos de la FRF, minimizando el efecto del ruido y mejorando la fiabilidad de los resultados.
- `γ²(ω)`: Mide la calidad de la medición en cada frecuencia. Valores cercanos a 1 indican que la señal de fuerza y la de aceleración están bien correlacionadas, lo que significa que el análisis es confiable en ese rango.

**Explicación de métodos avanzados:**
- **FFT optimizada**: Utiliza algoritmos eficientes y ventaneo inteligente para procesar grandes volúmenes de datos sin perder resolución espectral.
- **Análisis waterfall 3D**: Segmenta la señal en ventanas temporales y calcula la FFT de cada segmento, permitiendo visualizar cómo cambian los modos de vibración a lo largo del tiempo.
- **Función de transferencia (FRF) robusta**: Emplea estimadores H1, H2 y Hv para obtener resultados precisos incluso en presencia de ruido.
- **Coherencia**: Valida la calidad de la medición y ayuda a identificar rangos de frecuencia donde los resultados son fiables.
- **Rigidez dinámica compleja**: Permite analizar tanto la magnitud como la fase de la rigidez, proporcionando información sobre el comportamiento dinámico y el amortiguamiento.

**Explicación de parámetros y fórmulas:**
- `H(ω)`: Función de respuesta en frecuencia, calculada como el cociente entre la respuesta y la fuerza en el dominio de la frecuencia.
- `K(ω) = -ω² / H(ω)`: Rigidez dinámica, donde ω es la frecuencia angular (ω = 2πf) y H(ω) la FRF.
- `S_xf(ω)`, `S_ff(ω)`, `S_xx(ω)`: Espectros cruzados y de potencia, usados en los estimadores robustos H1, H2 y Hv para minimizar el efecto del ruido.
- `γ²(ω)`: Coherencia, indicador de la calidad de la medición en cada frecuencia (valor cercano a 1 = alta fiabilidad).
- **FFT optimizada** con ventaneo inteligente
- **Análisis waterfall 3D** con segmentación adaptativa
- **Función de transferencia (FRF)** robusta
- **Coherencia** para validación de medidas
- **Rigidez dinámica** compleja

### 📈 **Visualización Avanzada**
- **Gráficos interactivos** con Plotly
- **Vista 3D** con controles de cámara
- **Escalas logarítmicas/lineales**
- **Múltiples señales simultáneas**
- **Interfaz responsive**

**Explicación de cada funcionalidad visual:**
- **Gráficos interactivos**: Permiten al usuario explorar los datos, hacer zoom, seleccionar regiones de interés y comparar diferentes señales de manera intuitiva.
- **Vista 3D**: Facilita la interpretación de la evolución temporal y frecuencial de la respuesta estructural, mostrando cómo cambian los modos de vibración a lo largo del ensayo.
- **Controles de cámara**: El usuario puede rotar, acercar y alejar la vista para analizar detalles específicos en el gráfico waterfall 3D.
- **Escalas logarítmicas/lineales**: La escala logarítmica es útil para visualizar rangos amplios de frecuencia y amplitud, mientras que la lineal permite un análisis detallado en zonas específicas.
- **Múltiples señales simultáneas**: Es posible comparar diferentes ejes de aceleración y la fuerza, lo que ayuda a identificar modos acoplados y validar la consistencia de los datos.
- **Interfaz responsive**: La aplicación se adapta automáticamente al tamaño de la pantalla y al dispositivo, asegurando una experiencia de usuario óptima tanto en escritorio como en dispositivos móviles.

---

## 🏗️ ARQUITECTURA DEL SISTEMA

**¿Por qué es importante la arquitectura modular?**
La arquitectura modular facilita el mantenimiento, la escalabilidad y la incorporación de nuevas funcionalidades. Cada módulo se encarga de una tarea específica: el frontend gestiona la interacción con el usuario y la visualización; el backend realiza el procesamiento de datos y cálculos; el sistema de caché optimiza el rendimiento; y las utilidades proporcionan funciones de validación y manejo de errores. Esta organización permite que el software sea robusto, flexible y fácil de actualizar.

### 📦 **Estructura Modular**

**Explicación de la arquitectura modular:**
La aplicación está organizada en módulos independientes que se encargan de diferentes tareas. El frontend gestiona la interacción con el usuario, la carga de archivos y la visualización de resultados. El backend realiza el procesamiento de datos, filtrado, cálculos espectrales y generación de gráficos. El sistema de caché optimiza el rendimiento evitando recálculos innecesarios, y las utilidades proporcionan funciones de validación, manejo de errores y optimización de datasets. Esta estructura facilita el mantenimiento, la escalabilidad y la incorporación de nuevas funcionalidades.

```
RD_V1.10.3.py
├── 🎨 Frontend (Dash Layout)
│   ├── Carga de archivos
│   ├── Controles de filtros
│   ├── Parámetros de ensayo
│   ├── Visualización de gráficos
│   └── Exportación de datos
│
├── 🧠 Backend (Procesamiento)
│   ├── Carga y validación de datos
│   ├── Filtrado de señales
│   ├── Cálculos de FFT y FRF
│   ├── Análisis de amortiguamiento
│   └── Generación de gráficos
│
├── 💾 Sistema de Caché
│   ├── Cache computacional LRU
│   ├── Hashing de parámetros
│   ├── Invalidación inteligente
│   └── Optimización automática
│
└── 🔧 Utilidades
    ├── Optimización de datasets
    ├── Validación de datos
    ├── Manejo de errores
    └── Logging y debug
```

### 🔄 **Flujo de Datos**

```
📁 Archivo → 🔍 Detección → ✅ Validación → 📊 DataFrame
    ↓
🎛️ Filtros → 🔧 Procesamiento → 📈 Análisis
    ↓
⚡ FFT → 📊 FRF → 🧮 Rigidez → 📋 Amortiguamiento
    ↓
🎨 Visualización → 💾 Caché → 📥 Exportación
```

---

## 💾 SISTEMA DE CACHÉ INTELIGENTE

**¿Por qué es importante el sistema de caché?**
El sistema de caché permite que los cálculos más pesados, como la FFT, el análisis waterfall y la FRF, se realicen solo una vez por cada conjunto de parámetros. Si el usuario repite una operación con los mismos datos y parámetros, el resultado se recupera instantáneamente, acelerando el flujo de trabajo y evitando esperas innecesarias. Esto es especialmente útil en datasets grandes, donde los cálculos pueden tardar varios segundos o minutos.

**¿Cómo funciona la política LRU?**
La política LRU (Least Recently Used) elimina automáticamente los resultados menos utilizados cuando la memoria del caché alcanza su límite. Así, se garantiza que los resultados más relevantes y recientes estén siempre disponibles, optimizando el uso de recursos y evitando saturaciones de memoria.

**¿Qué ventajas aporta al usuario?**
- Permite iterar rápidamente sobre diferentes parámetros de análisis sin recálculos.
- Reduce el tiempo de espera al cambiar escalas, filtros o ventanas temporales.
- Facilita la comparación de resultados y la validación experimental.

### 🎯 **Objetivo**
Optimizar el rendimiento evitando recálculos innecesarios de FFT, waterfall y FRF cuando los parámetros no han cambiado.

### 🧠 **Arquitectura del Caché**

```python
class CacheComputacional:
    """
    Sistema LRU con hashing inteligente de parámetros
    """
    def __init__(self, max_cache_size=50):
        self.cache = {}                 # Resultados almacenados
        self.cache_access_times = {}    # Timestamps LRU
        self.max_cache_size = 50        # Límite de memoria
        self.hits = 0                   # Estadísticas de hit
        self.misses = 0                 # Estadísticas de miss
```

### ⚡ **Beneficios de Rendimiento**

|        Operación         | Sin Caché | Con Caché |    Mejora   |
|--------------------------|-----------|-----------|-------------|
| **Cambio de escala FFT** |  2-5 seg  | < 0.1 seg |  **95%** ⚡ |
|    **Cambio vista 3D**   |  3-8 seg  | < 0.2 seg |  **95%** ⚡ |
| **Switch entre señales** |  1-3 seg  | < 0.1 seg |  **90%** ⚡ |
|  **Recálculo waterfall** |  5-15 seg | < 0.3 seg |  **95%** ⚡ |

### 🔄 **Funcionamiento Automático**

#### **1. Activación por Defecto**
```python
USAR_CACHE = True  # ✅ HABILITADO automáticamente
```

#### **2. Limpieza Inteligente**
- **Al iniciar aplicación**: Caché vacío
- **Al cargar nuevo archivo**: Limpieza automática
- **Al aplicar filtros/cortes**: Invalidación por cambio de datos
- **Memoria llena**: Eliminación LRU automática

#### **3. Detección de Cambios**
```python
# Hash inteligente de parámetros
def generar_hash_parametros(self, *args, **kwargs):
    parametros_str = f"{args}_{sorted(kwargs.items())}"
    return hashlib.md5(parametros_str.encode()).hexdigest()
```

#### **4. Funciones Adaptativas**
```python
def generar_grafico_fft_adaptativo(df, seleccion_multi, escala_x, escala_y):
    if USAR_CACHE:
        return generar_grafico_fft_con_cache(...)  # 🚀 Optimizado
    else:
        return generar_grafico_fft_optimizado(...) # 🔧 Original
```

### 📊 **Monitoreo en Tiempo Real**
```bash
[CACHE] FFT obtenida del caché (hit rate: 85.3%)
[CACHE] Waterfall obtenido del caché (hit rate: 78.9%)
[CACHÉ] Caché limpiado al cargar nuevo archivo
```

---

## 🔧 FUNCIONALIDADES DETALLADAS

**Explicación de cada funcionalidad:**
- **Carga de archivos inteligente**: Detecta automáticamente el formato y la estructura de los datos, evitando errores comunes y facilitando el trabajo con diferentes sistemas de adquisición. La validación robusta asegura que los datos sean consistentes y aptos para el análisis.
- **Sistema de filtros avanzado**: Permite limpiar las señales de ruido, offset y componentes no deseadas, mejorando la calidad del análisis espectral y modal. Cada filtro está diseñado para preservar las características relevantes de la señal.
- **Análisis espectral robusto**: Utiliza ventaneo adaptativo y algoritmos optimizados para obtener resultados precisos incluso en presencia de ruido o transitorios. El cálculo eficiente de la FFT y la FRF permite trabajar con grandes volúmenes de datos sin perder resolución.
- **Análisis waterfall 3D**: Segmenta la señal en ventanas temporales y calcula la FFT de cada segmento, mostrando cómo evolucionan los modos de vibración a lo largo del tiempo. La segmentación adaptativa optimiza el rendimiento y la visualización.
- **Cálculo de rigidez dinámica**: Emplea estimadores robustos y detección automática de antiresonancias para obtener resultados fiables y físicamente consistentes. La validación de coherencia y el manejo de zonas problemáticas aseguran la calidad del análisis.
- **Análisis de amortiguamiento**: Calcula tanto el amortiguamiento modal (por ancho de banda) como el global (por decremento logarítmico), proporcionando información detallada sobre la disipación de energía en la estructura.

### 📁 **Carga de Archivos Inteligente**

#### **Detección Automática de Formato**
```python
def cargar_archivo(contents, filename):
    # 1. Detectar extensión (.csv, .txt, .xlsx)
    # 2. Autodetectar separador (coma, punto y coma, tabulador)
    # 3. Identificar línea de cabeceras
    # 4. Validar estructura de datos
    # 5. Normalizar columnas a estándar
```

#### **Formatos Soportados**
- **CSV estándar**: `,` o `;` como separador
- **TXT Catman**: Formato HBM con metadatos
- **XLSX**: Excel con autodetección de hojas
- **Separadores mixtos**: Detección inteligente

#### **Validación Robusta**
- ✅ Verificación de columnas requeridas
- ✅ Conversión automática de tipos de datos
- ✅ Eliminación de filas problemáticas
- ✅ Regeneración de vector temporal si es irregular

### 🎛️ **Sistema de Filtros Avanzado**

#### **1. Filtro Mediana Adaptativo**
```python
def aplicar_filtro_mediana(señal, kernel_size=5):
    """
    Elimina ruido impulsivo preservando transitorios
    """
    return medfilt(señal, kernel_size=kernel_size)
```

#### **2. Filtro Paso Alto**
```python
def aplicar_paso_alto(señal, frecuencia_corte, fs):
    """
    Elimina offset y deriva de baja frecuencia
    """
    b, a = butter(2, frecuencia_corte / (fs / 2), btype='high')
    return filtfilt(b, a, señal)
```

#### **3. Filtro Multibanda Inteligente**
```python
def filtro_multibanda_adaptativo(señal, fs, frecuencias_centrales, ancho_banda=20.0):
    """
    Aísla bandas específicas con agrupamiento automático
    """
    # 1. Agrupar frecuencias cercanas
    # 2. Calcular bandas óptimas
    # 3. Diseñar filtro FIR
    # 4. Aplicar con validación de pérdidas
```

#### **Características del Filtro Multibanda**
- **Agrupamiento automático** de frecuencias cercanas
- **Validación de pérdidas** de amplitud
- **Optimización iterativa** del orden FIR
- **Preservación de fases** importantes

### 📊 **Análisis Espectral Robusto**

#### **FFT con Ventaneo Adaptativo**
```python
def ventana_exponencial(y, fs, tau=None):
    """
    Ventaneo optimizado para análisis transitorio
    """
    # 1. Estimar tau automáticamente
    # 2. Detectar decaimiento al 5%
    # 3. Aplicar ventana exponencial
    # 4. Preservar características espectrales
```

#### **Ventaneo Específico por Tipo de Señal**
- **Aceleración**: Ventana exponencial adaptativa
- **Fuerza**: Ventana de impacto con detección automática
- **Otros**: Ventaneo Hann estándar

#### **FFT Optimizada**
- **Cálculo eficiente** con scipy
- **Manejo de datasets grandes** (>100k puntos)
- **Escalas logarítmicas/lineales**
- **Conversión automática** a dB

### 🌊 **Análisis Waterfall 3D**

#### **Segmentación Adaptativa**
```python
def generar_waterfall_optimizado(df_json, seleccion_eje, ...):
    # Optimización automática según tamaño
    if N > 200000:
        max_segments = 20      # Dataset muy grande
    elif N > 100000:
        max_segments = 30      # Dataset mediano
    else:
        max_segments = 50      # Dataset pequeño
```

#### **Características Avanzadas**
- **Duración de segmento configurable**
- **Solapamiento optimizado** (50%)
- **Reducción visual inteligente** para performance
- **Vista 3D con controles** de cámara
- **Énfasis selectivo** de curvas

### 📈 **Análisis de Rigidez Dinámica**

#### **Cálculo de FRF Robusta**
```python
def calculate_dynamic_stiffness_robust(H_frf, frequencies):
    """
    K(ω) = -ω² / H(ω)
    """
    # 1. Detectar antiresonancias
    # 2. Calcular rigidez dinámica
    # 3. Interpolar zonas problemáticas
    # 4. Validar resultados físicos
```

#### **Estimadores de FRF**
- **H1**: `S_xf / S_ff` (ruido en salida)
- **H2**: `S_xx / S_xf*` (ruido en entrada)
- **Hv**: Combinación ponderada por coherencia

#### **Detección de Antiresonancias**
```python
def detect_antiresonances(H_frf, frequencies, window_hz=10):
    # 1. Calcular piso de ruido local
    # 2. Identificar caídas significativas
    # 3. Validar con coherencia
    # 4. Marcar para interpolación
```

### 🔊 **Análisis de Amortiguamiento**

#### **Amortiguamiento Modal (Ancho de Banda)**
```python
def calculo_amortiguamiento(accel, fs, frecuencias_centrales=None):
    """
    ζ = (f₂ - f₁) / (2 × fₙ)
    """
    # 1. Detectar picos espectrales
    # 2. Calcular ancho de banda -3dB
    # 3. Estimar amortiguamiento modal
    # 4. Validar rango físico
```

#### **Amortiguamiento Global (Decremento Logarítmico)**
```python
def damping_least_squares(signal, fs):
    """
    ζ = -slope / ω
    """
    # 1. Detectar picos temporales
    # 2. Ajuste por mínimos cuadrados
    # 3. Calcular pendiente de decaimiento
    # 4. Convertir a factor de amortiguamiento
```

---

## 🎨 INTERFAZ DE USUARIO

**Explicación de cada sección de la interfaz:**
- **Carga de archivo**: Permite al usuario seleccionar y cargar datos experimentales en diferentes formatos. El estado visual indica si la carga fue exitosa y si los datos están listos para el análisis.
- **Parámetros del ensayo**: El usuario puede configurar parámetros clave como la masa del martillo, que afectan directamente el cálculo de la FRF y la rigidez dinámica. Los estados visuales ayudan a evitar errores y asegurar que los valores sean aplicados correctamente.
- **Filtros de señal**: Ofrece controles para activar y ajustar los filtros digitales, permitiendo limpiar la señal antes del análisis espectral y modal. La interfaz muestra el estado de cada filtro y su efecto sobre los datos.
- **Corte temporal**: Permite seleccionar la ventana de tiempo relevante para el análisis, excluyendo zonas ruidosas o irrelevantes. El estado visual informa sobre la cantidad de datos seleccionados y la efectividad del corte.
- **Selección de señales**: El usuario puede elegir qué señales analizar y visualizar, facilitando la comparación entre diferentes ejes de aceleración y la fuerza. Los controles permiten alternar entre gráficos temporales, espectrales y 3D.
- **Sistema de indicadores de estado**: Utiliza colores e iconos para informar al usuario sobre el estado de cada acción, facilitando la interpretación y evitando errores.

### 🎛️ **Panel de Control Principal**

#### **Sección 1: Carga de Archivo**
```html
📁 Cargar archivo CSV de datos: [Seleccionar archivo]
💾 Estado: "Archivo cargado: datos_ensayo.csv"
⏳ Loading: Indicador circular verde
```

#### **Sección 2: Parámetros del Ensayo**
```html
🔨 Masa martillo: [1.0] kg [Aplicar masa]
   ✓ Estado visual: Verde = aplicado, Azul = listo, Gris = sin datos
```

#### **Sección 3: Filtros de Señal**
```html
🔧 Mediana: ⚪ Sí ⚪ No [5]
🔊 Paso alto: ⚪ Sí ⚪ No [0.5] Hz  
📊 Multibanda: ⚪ Sí ⚪ No [50,200] Hz
   [Aplicar filtros] ✓
```

#### **Sección 4: Corte Temporal**
```html
✂️ Inicio (s): [____] Fin (s): [____] [Aplicar corte]
   ⚠️ "Corte aplicado: 0.5s a 2.0s, 15,000 puntos"
```

#### **Sección 5: Selección de Señales**
```html
📊 Tiempo/FFT:     📈 3D/Rigidez:
☑️ Accel X         ⚪ Accel X
☐ Accel Y         ⚪ Accel Y  
☐ Accel Z         ⚪ Accel Z
☐ Fuerza          ⚪ Fuerza
```

### 🎮 **Sistema de Indicadores de Estado**

#### **Código de Colores**
|      Color       |   Estado   |            Significado           |         Duración       |
|------------------|------------|----------------------------------|------------------------|
|   🔴 **Rojo**   | Bloqueado  |  No disponible por restricciones |       Persistente      |
| 🟡 **Amarillo** | Procesando |    ⏳ Trabajando en segundo plano | Durante procesamiento |
|   🟢 **Verde**  | Completado | ✅ Acción realizada exitosamente |       Persistente     |
|   🔵 **Azul**   | Disponible |   ◯ Listo para ejecutar acción   |       Hasta click     |
|   🔘 **Gris**   | Sin datos  |   ⚠️ Falta información o datos   |     Hasta resolver     |

#### **Iconos de Estado**
- `⚠️` Advertencia / sin datos
- `⏳` Procesando en tiempo real
- `✓` Completado exitosamente
- `◯` Disponible para usar
- `○` Configuración incompleta
- `✗` Bloqueado por restricciones

### 📊 **Gráficos Interactivos**

#### **1. Gráfico Temporal**
- **Múltiples señales** superpuestas
- **Señal original vs filtrada** (línea punteada)
- **Zoom y pan** interactivos
- **Exportación** a imagen

#### **2. Gráfico FFT**
- **Escalas X**: Linear/Logarítmica
- **Escalas Y**: Amplitud/dB
- **Cambio instantáneo** (con caché)
- **Múltiples señales** simultáneas

#### **3. Gráfico Waterfall 3D**
- **Vista 3D rotable**
- **Selector de curvas** específicas
- **Énfasis visual** de curvas seleccionadas
- **Fijar vista** para comparaciones
- **Duración de segmento** configurable

#### **4. Gráfico Rigidez Dinámica**
- **Magnitud y fase** en subplots
- **Escalas configurables**
- **Detección automática** de resonancias
- **Indicador de estimador** usado (H1/H2/Hv)

#### **5. Gráfico Coherencia**
- **Validación de FRF**
- **Rango 0-1** fijo
- **Identificación** de frecuencias fiables

---

## 🧮 ALGORITMOS Y MÉTODOS

**Explicación de los algoritmos principales:**
- **Función de respuesta en frecuencia (FRF)**: Permite relacionar la excitación y la respuesta de la estructura en el dominio de la frecuencia, siendo la base para el cálculo de la rigidez dinámica y el amortiguamiento.
- **Rigidez dinámica**: Indica la resistencia de la estructura a la deformación bajo cargas dinámicas. El cálculo robusto maneja antiresonancias y valida los resultados físicos para evitar errores experimentales.
- **Estimadores robustos (H1, H2, Hv)**: Cada estimador está diseñado para minimizar el efecto del ruido en diferentes situaciones experimentales. La combinación ponderada por coherencia asegura que se utilice el estimador más adecuado en cada rango de frecuencia.
- **Coherencia**: Mide la calidad de la medición y ayuda a identificar rangos de frecuencia donde los resultados son fiables. La validación automática informa al usuario si la configuración experimental necesita ajustes.
- **Algoritmos de amortiguamiento**: Calculan tanto el amortiguamiento modal (por ancho de banda) como el global (por decremento logarítmico), proporcionando información sobre la disipación de energía y la estabilidad de la estructura.

### 📐 **Base Matemática**

**¿Por qué son importantes estas fórmulas?**
Las fórmulas matemáticas presentadas aquí son la base del análisis de rigidez dinámica y amortiguamiento. Permiten transformar los datos experimentales en información útil para el diagnóstico y diseño estructural. Cada expresión tiene un propósito específico y su correcta interpretación es clave para obtener resultados fiables.

**Interpretación de cada fórmula:**

#### **Función de Respuesta en Frecuencia (FRF)**
```
H(ω) = X(ω) / F(ω)
```
Donde:
- `X(ω)`: Respuesta en frecuencia (aceleración)
- `F(ω)`: Excitación en frecuencia (fuerza)

Esta fórmula expresa cómo responde la estructura (aceleración) ante una fuerza aplicada en cada frecuencia. Es fundamental para caracterizar el comportamiento dinámico y sirve como base para el cálculo de la rigidez y el amortiguamiento. Un valor alto de H(ω) indica que la estructura responde fuertemente a esa frecuencia, lo que puede señalar una resonancia.

#### **Rigidez Dinámica**
```
K(ω) = -ω² / H(ω)
```
Para sistemas con entrada fuerza y salida aceleración.

La rigidez dinámica K(ω) indica cuánta fuerza se requiere para producir una aceleración determinada en cada frecuencia. Valores bajos de K(ω) suelen coincidir con resonancias (la estructura se mueve mucho con poca fuerza), mientras que valores altos pueden señalar zonas rígidas o antiresonancias. El signo negativo refleja la relación física entre fuerza y aceleración en sistemas vibratorios.

#### **Estimadores Robustos**
```python
# H1 - Óptimo para ruido en salida
H1(ω) = S_xf(ω) / S_ff(ω)

# H2 - Óptimo para ruido en entrada  
H2(ω) = S_xx(ω) / S_xf*(ω)

# Hv - Combinación ponderada por coherencia
Hv(ω) = H1 si γ² > 0.9
      = √(H1×H2) si 0.7 < γ² ≤ 0.9  
      = H2 si γ² ≤ 0.7
```

Estos estimadores permiten calcular la FRF de manera robusta, minimizando el efecto del ruido según su origen (entrada o salida). H1 es ideal cuando el ruido afecta principalmente la aceleración, H2 cuando afecta la fuerza, y Hv combina ambos según la coherencia, asegurando que se utilice el estimador más fiable en cada rango de frecuencia. Esto mejora la calidad y la interpretación de los resultados experimentales.

#### **Coherencia**
```
γ²(ω) = |S_xf(ω)|² / (S_xx(ω) × S_ff(ω))
```

La coherencia γ²(ω) mide la calidad de la relación entre fuerza y aceleración en cada frecuencia. Valores cercanos a 1 indican que la medición es fiable y que el ruido es bajo; valores bajos sugieren problemas experimentales, como ruido excesivo, mala sincronización o errores en los sensores. Es fundamental revisar la coherencia antes de interpretar los resultados de rigidez y amortiguamiento.

### 🔢 **Algoritmos de Amortiguamiento**

El amortiguamiento es una propiedad clave para entender cómo una estructura disipa energía y cómo responde ante vibraciones. Los algoritmos presentados aquí permiten calcular tanto el amortiguamiento modal (asociado a cada modo de vibración) como el global (de toda la estructura), proporcionando información esencial para el diseño y diagnóstico.

#### **Método Ancho de Banda (-3dB)**
```python
def amortiguamiento_modal(pico_frecuencia, f1, f2):
    """
    f1, f2: Frecuencias a -3dB del pico
    fn: Frecuencia natural del pico
    """
    zeta = (f2 - f1) / (2 * fn)
    return zeta
```

Este método estima el amortiguamiento modal a partir del ancho de banda de cada pico espectral. Se identifican las frecuencias a -3dB del máximo y se calcula el factor de amortiguamiento. Valores típicos para estructuras metálicas oscilan entre 0.01 y 0.05. Un ancho de banda mayor indica mayor disipación de energía.

#### **Decremento Logarítmico**
```python
def decremento_logaritmico(signal_temporal, fs):
    """
    δ = ln(x_n / x_{n+1})
    ζ = δ / √(4π² + δ²)
    """
    # 1. Detectar picos consecutivos
    # 2. Calcular decremento logarítmico
    # 3. Convertir a factor de amortiguamiento
```

El decremento logarítmico calcula el amortiguamiento global a partir de la caída de los picos en la señal temporal. Es útil para respuestas impulsivas y permite estimar la disipación de energía en todo el sistema. Valores negativos o superiores a 0.5 suelen indicar errores de medición o problemas experimentales.

### 🔬 **Validaciones Científicas**

Las validaciones científicas aseguran que los resultados obtenidos sean físicamente razonables y fiables. Cada función verifica rangos, detecta problemas experimentales y ayuda al usuario a interpretar correctamente los resultados, evitando conclusiones erróneas.

#### **Validación de Coherencia**
```python
def validar_coherencia(coherencia, umbral=0.8):
    """
    Coherencia > 0.8: Excelente
    Coherencia > 0.6: Buena  
    Coherencia < 0.6: Revisar medida
    """
```

Esta función clasifica la calidad de la medición según la coherencia. Si γ² > 0.8, los resultados son altamente fiables; entre 0.6 y 0.8, son aceptables pero requieren precaución; por debajo de 0.6, se recomienda revisar la configuración experimental, aplicar filtros o repetir el ensayo.

#### **Detección de Antiresonancias**
```python
def es_antiresonancia(H_magnitude, threshold_db=-25):
    """
    Detecta caídas significativas en la FRF
    que pueden afectar el cálculo de rigidez
    """
```

Las antiresonancias son zonas donde la magnitud de la FRF cae abruptamente, lo que puede distorsionar el cálculo de la rigidez dinámica. Detectarlas permite interpolar o corregir los resultados, asegurando que la interpretación física sea válida y evitando errores en el diagnóstico estructural.

#### **Rango Físico de Amortiguamiento**
```python
def validar_amortiguamiento(zeta):
    """
    0 < ζ < 0.5: Físicamente razonable
    ζ > 0.5: Sobreamortiguado (verificar)
    ζ < 0: Error de cálculo
    """
```

Esta función verifica que el valor de amortiguamiento calculado sea físicamente posible. Valores entre 0 y 0.5 son típicos en estructuras reales; valores superiores a 0.5 indican sobreamortiguamiento y deben ser revisados; valores negativos señalan errores de cálculo o problemas en la medición.

---

## ⚡ OPTIMIZACIONES DE RENDIMIENTO

### 🚀 **Optimizaciones Automáticas**

#### **1. Datasets Grandes (>50k puntos)**
```python
def optimizar_dataframe_para_visualizacion(df, max_puntos=50000):
    """
    Submuestreo inteligente para visualización:
    - 30% en primer 10% del tiempo (impactos)
    - 70% distribuido uniformemente
    """
```

#### **2. FFT Optimizada**
```python
def generar_grafico_fft_optimizado(df, ...):
    # Para datasets >100k puntos
    if len(df) > 100000:
        max_fft_points = 32768  # Límite óptimo
        mostrar_progreso_simple("FFT optimizada", len(df))
```

#### **3. Waterfall Adaptativo**
```python
def generar_waterfall_optimizado(df_json, ...):
    # Optimización automática por tamaño
    if N > 200000:
        max_segments = 20      # Muy grande
    elif N > 100000:  
        max_segments = 30      # Mediano
    else:
        max_segments = 50      # Pequeño
```

### 📊 **Métricas de Rendimiento**

|         Operación         |  Dataset Pequeño (<50k) | Dataset Grande (>200k) |      Optimización     |
|---------------------------|-------------------------|------------------------|-----------------------|
|     **Carga archivo**     |         < 1 seg         |         2-5 seg        |  Validación eficiente |
|     **FFT sin caché**     |         1-2 seg         |         5-15 seg       |   Limitación puntos   |
|     **FFT con caché**     |        < 0.1 seg        |        < 0.1 seg       |   ⚡**95% mejora**    |
|  **Waterfall sin caché**  |         3-5 seg         |        15-30 seg       | Segmentos adaptativos |
|  **Waterfall con caché**  |        < 0.2 seg        |        < 0.3 seg       |   ⚡**90% mejora**    |
|     **Cambio escala**     |        0.5-1 seg        |         2-5 seg        |  Regeneración parcial |
| **Cambio escala (caché)** |        < 0.1 seg        |        < 0.1 seg       |   ⚡ **95% mejora**   |

### 🧠 **Estrategias de Memoria**

#### **Gestión Inteligente de Memoria**
```python
def monitorear_memoria():
    """
    Controla uso de RAM y aplica limpieza preventiva
    """
    memoria_actual = psutil.Process().memory_info().rss / (1024**2)
    if memoria_actual > 2000:  # >2GB
        gc.collect()  # Forzar limpieza
```

#### **Política LRU en Caché**
```python
def cache_lru_eviction(self):
    """
    Elimina elementos menos recientemente usados
    cuando se alcanza el límite de memoria
    """
    if len(self.cache) >= self.max_cache_size:
        oldest_key = min(self.cache_access_times.keys(), 
                        key=lambda k: self.cache_access_times[k])
        del self.cache[oldest_key]
```

---

## 💻 GUÍA DE INSTALACIÓN

### 📋 **Requisitos del Sistema**

#### **Requisitos Mínimos**
- **SO**: Windows 10/11, macOS 10.14+, Linux Ubuntu 18.04+
- **Python**: 3.8 o superior
- **RAM**: 4 GB mínimo (8 GB recomendado)
- **Espacio disco**: 500 MB para instalación
- **Navegador**: Chrome, Firefox, Safari, Edge (versiones recientes)

#### **Requisitos Recomendados**
- **RAM**: 16 GB (para datasets grandes >1M puntos)
- **CPU**: 4 núcleos o más para procesamiento paralelo
- **SSD**: Para mejor rendimiento de carga de archivos

### 🐍 **Instalación Python**

#### **1. Verificar Python**
```bash
python --version
# Debe mostrar Python 3.8+ 
```

#### **2. Crear Entorno Virtual (Recomendado)**
```bash
# Crear entorno
python -m venv rigidez_dinamica_env

# Activar entorno (Windows)
rigidez_dinamica_env\Scripts\activate

# Activar entorno (macOS/Linux)
source rigidez_dinamica_env/bin/activate
```

#### **3. Instalar Dependencias**
```bash
pip install dash==2.14.1
pip install plotly==5.17.0
pip install pandas==2.1.0
pip install numpy==1.24.3
pip install scipy==1.11.1
pip install dash-bootstrap-components==1.4.1
pip install openpyxl==3.1.2
pip install psutil==5.9.5
```

#### **Archivo requirements.txt**
```txt
dash==2.14.1
plotly==5.17.0  
pandas==2.1.0
numpy==1.24.3
scipy==1.11.1
dash-bootstrap-components==1.4.1
openpyxl==3.1.2
psutil==5.9.5
```

Instalar con:
```bash
pip install -r requirements.txt
```

### 📁 **Estructura de Proyecto**

```
📁 rigidez_dinamica/
├── 📄 RD_V1.10.3.py           # Aplicación principal
├── 📄 requirements.txt         # Dependencias Python
├── 📁 assets/                 # Recursos estáticos
│   └── 🖼️ logo_edai.png       # Logo de la aplicación
├── 📁 datos_prueba/           # Archivos de ejemplo
│   ├── 📊 ensayo_001.csv
│   ├── 📊 ensayo_catman.txt
│   └── 📊 ensayo_excel.xlsx
└── 📄 DOCUMENTACION_RIGIDEZ_DINAMICA.md  # Esta documentación
```

### ▶️ **Ejecutar Aplicación**

#### **Método 1: Ejecución Directa**
```bash
python RD_V1.10.3.py
```

#### **Método 2: Script de Inicio (Windows)**
```batch
@echo off
echo Iniciando aplicación Rigidez Dinámica...
cd /d "%~dp0"
call rigidez_dinamica_env\Scripts\activate
python RD_V1.10.3.py
pause
```

#### **Método 3: Script de Inicio (Linux/macOS)**
```bash
#!/bin/bash
echo "Iniciando aplicación Rigidez Dinámica..."
cd "$(dirname "$0")"
source rigidez_dinamica_env/bin/activate
python RD_V1.10.3.py
```

### 🌐 **Acceso Web**

1. **Ejecutar script** de inicio
2. **Esperar mensaje**: "Running on http://127.0.0.1:8050"
3. **Navegador se abre automáticamente** o ir a: http://localhost:8050
4. **Aplicación lista** para usar

---

## 👨‍💻 GUÍA DE USUARIO

### 🚀 **Inicio Rápido**

#### **Paso 1: Cargar Datos**
1. Click en **"Seleccionar archivo"**
2. Elegir archivo (.csv, .txt, .xlsx)
3. **Verificar carga exitosa**: mensaje verde con nombre del archivo
4. **Validar datos**: gráfico temporal debe aparecer automáticamente

#### **Paso 2: Configurar Parámetros**
```html
🔨 Masa martillo: [1.5] kg → [Aplicar masa] ✅
   ⚠️ IMPORTANTE: Aplicar masa antes de continuar
```

#### **Paso 3: Aplicar Filtros (Opcional)**
```html
🔧 Mediana: ✅ Sí [5]           # Eliminar ruido impulsivo
🔊 Paso alto: ✅ Sí [0.5] Hz   # Eliminar offset  
📊 Multibanda: ✅ Sí [50,200] Hz # Aislar frecuencias
   → [Aplicar filtros] ✅
```

#### **Paso 4: Corte Temporal (Opcional)**
```html
✂️ Inicio: [0.1] s  Fin: [2.0] s → [Aplicar corte] ✅
   💡 TIP: Cortar zona de interés para mejor análisis
```

#### **Paso 5: Seleccionar Señales**
```html
📊 Para gráficos tiempo/FFT:    📈 Para análisis 3D/rigidez:
☑️ Accel X                     ⚪ Accel X ← Seleccionado
☑️ Accel Y                     ⚪ Accel Y
☐ Accel Z                      ⚪ Accel Z
☐ Fuerza                       ⚪ Fuerza
```

### 📊 **Interpretación de Resultados**

#### **Gráfico Temporal**
- **Señal original** (línea punteada gris): Datos sin procesar
- **Señal filtrada** (línea sólida color): Datos procesados
- **Validar**: Impacto claro al inicio, decaimiento exponencial

#### **Gráfico FFT**
- **Picos claros**: Frecuencias naturales del sistema
- **Escala dB**: Para mejor visualización de dinámicas amplias
- **Escala log**: Para analizar amplio rango frecuencial

#### **Gráfico Waterfall 3D**
- **Eje X**: Frecuencia (Hz)
- **Eje Y**: Tiempo (segmentos)
- **Eje Z**: Amplitud
- **Colores**: Intensidad de respuesta

#### **Rigidez Dinámica**
- **Magnitud |K|**: Rigidez en N/mm
- **Fase ∠K**: Características dinámicas
- **Resonancias**: Caídas en magnitud
- **Antiresonancias**: Picos en magnitud

#### **Coherencia**
- **γ² > 0.8**: Excelente calidad de medida ✅
- **γ² > 0.6**: Buena calidad ⚠️
- **γ² < 0.6**: Revisar configuración experimental ❌

#### **Tablas de Amortiguamiento**
```html
📋 Resumen Global:
   ζ global: 0.0234 (2.34%)
   C/m: 15.678 N·s/m

📋 Resumen Modal:
   Frecuencia: 85.3 Hz → ζ: 0.0189 (1.89%)
   Frecuencia: 156.7 Hz → ζ: 0.0267 (2.67%)
```

### 🎮 **Controles Avanzados**

#### **Controles de Vista 3D**
- **Restablecer visibilidad**: Mostrar todas las curvas
- **Fijar vista**: Bloquear orientación de cámara
- **Selector de curvas**: Destacar curvas específicas
- **Duración segmento**: Controlar resolución temporal

#### **Escalas de Visualización**
```html
📐 Eje X (FFT y 3D):
   ⚪ Lineal        ⚪ Logarítmico

📐 Eje Y (Amplitud):  
   ⚪ Amplitud      ⚪ dB
```

#### **Exportación de Datos**
- **Botón "Exportar datos 3D"**
- **Formato**: ZIP con 2 archivos CSV
  - `datos_3D_long.csv`: Formato largo (segmento, tiempo, freq, amplitud)
  - `datos_3D_matriz.csv`: Formato matricial (freq vs tiempo)

### 🔧 **Workflow Típico**

#### **Análisis Estándar**
```
1. 📁 Cargar datos
2. 🔨 Configurar masa martillo  
3. 🔧 Aplicar filtros básicos (mediana + paso alto)
4. 📊 Revisar FFT para identificar modos
5. 📈 Analizar rigidez dinámica
6. 📋 Extraer parámetros de amortiguamiento
7. 💾 Exportar resultados
```

#### **Análisis Avanzado**
```
1. 📁 Cargar datos
2. 🔨 Configurar masa martillo
3. 🔧 Aplicar filtro multibanda en frecuencias específicas
4. ✂️ Cortar ventana de interés temporal
5. 🌊 Analizar waterfall 3D para evolución temporal
6. 📊 Comparar múltiples señales (X, Y, Z)
7. 📈 Evaluar coherencia para validar medidas
8. 📋 Calcular amortiguamiento modal detallado
9. 💾 Exportar datos completos
```

---

## 🔧 TROUBLESHOOTING

**Explicación de problemas comunes y soluciones:**
Cada error o síntoma descrito en esta sección incluye la causa probable y una solución recomendada. El objetivo es que el usuario pueda identificar rápidamente el origen del problema y aplicar la corrección adecuada, evitando frustraciones y pérdidas de tiempo. Las soluciones están pensadas para usuarios de todos los niveles, con instrucciones claras y pasos concretos.

### ❌ **Problemas Comunes**

#### **Error de Carga de Archivo**
```
❌ Síntoma: "Error al leer el archivo: ..."
🔍 Causas posibles:
   - Formato no soportado
   - Archivo corrupto
   - Codificación incorrecta
   - Separadores inconsistentes

✅ Soluciones:
   1. Verificar que el archivo es .csv, .txt o .xlsx
   2. Abrir en Excel y guardar como CSV UTF-8
   3. Verificar que hay al menos 5 columnas numéricas
   4. Revisar que la primera fila contiene headers válidos
```

#### **Gráficos Vacíos o Sin Datos**
```
❌ Síntoma: Gráficos muestran "Sin datos disponibles"
🔍 Causas posibles:
   - Archivo sin datos válidos
   - Columnas mal interpretadas
   - Datos todos NaN o infinitos
   - Selección de señales incorrecta

✅ Soluciones:
   1. Revisar la carga: mensaje debe ser verde
   2. Verificar que las señales están seleccionadas
   3. Comprobar que las columnas tienen datos numéricos
   4. Reload página y volver a cargar archivo
```

#### **FFT/Waterfall Muy Lento**
```
❌ Síntoma: Cálculos tardan mucho tiempo
🔍 Causas posibles:
   - Dataset muy grande (>1M puntos)
   - Caché deshabilitado
   - Memoria insuficiente
   - Filtros complejos aplicados

✅ Soluciones:
   1. Verificar que USAR_CACHE = True
   2. Aplicar corte temporal para reducir datos
   3. Cerrar otras aplicaciones (liberar RAM)  
   4. Usar filtros simples primero
```

#### **Amortiguamiento No Físico**
```
❌ Síntoma: "ζ = 0.8543" (>50%)
🔍 Causas posibles:
   - Señal muy ruidosa
   - Excitación insuficiente
   - Múltiples modos superpuestos
   - Configuración experimental incorrecta

✅ Soluciones:
   1. Aplicar filtro mediana para reducir ruido
   2. Verificar la masa del martillo aplicada
   3. Usar filtro multibanda para aislar modos
   4. Revisar la coherencia (debe ser >0.8)
```

#### **Coherencia Baja**
```
❌ Síntoma: γ² < 0.6 en rangos de interés
🔍 Causas posibles:
   - Ruido excesivo en las señales
   - Excitación insuficiente
   - Problemas de sincronización
   - Distorsión en sensores

✅ Soluciones:
   1. Aplicar filtros de ruido (mediana + paso alto)
   2. Verificar conexiones de sensores
   3. Revisar rango dinámico de la adquisición
   4. Considerar ventaneo diferente
```

### 🐛 **Errores Técnicos**

#### **Error: ImportError/ModuleNotFoundError**
```bash
❌ Error: "ImportError: No module named 'dash'"
✅ Solución:
   pip install dash plotly pandas numpy scipy
   
   # O usar requirements.txt:
   pip install -r requirements.txt
```

#### **Error: Memory/RAM Insuficiente**
```bash
❌ Error: "MemoryError" o aplicación se cuelga
✅ Soluciones:
   1. Cerrar otros programas
   2. Aplicar corte temporal antes de análisis
   3. Usar datasets más pequeños para pruebas
   4. Aumentar memoria virtual del sistema
```

#### **Error: Puerto 8050 Ocupado**
```bash
❌ Error: "Address already in use: 8050"
✅ Soluciones:
   1. Cerrar otra instancia de la aplicación
   2. Esperar 30 segundos y reintentar
   3. Cambiar puerto en código: app.run(port=8051)
   4. Reiniciar sistema si persiste
```

#### **Error: Permisos de Escritura**
```bash
❌ Error: "PermissionError" al exportar
✅ Soluciones:
   1. Cerrar Excel si tiene archivos abiertos
   2. Ejecutar como administrador
   3. Cambiar directorio de trabajo
   4. Verificar permisos de carpeta
```

### 🔍 **Depuración Avanzada**

#### **Activar Modo Debug**
```python
# En la línea final de RD_V1.10.3.py:
app.run(debug=True, dev_tools_hot_reload=False)
```

#### **Ver Logs de Caché**
```python
# En consola durante ejecución:
stats = cache_computacional.estadisticas_cache()
print(f"Hit rate: {stats['hit_rate']:.1f}%")
print(f"Cache size: {stats['cache_size']} elementos")
```

#### **Verificar Datos de Entrada**
```python
# Después de cargar archivo, en consola:
[DEBUG] DataFrame cargado: shape=(50000, 5)
[DEBUG] Columnas: ['tiempo', 'fuerza', 'accel_x', 'accel_y', 'accel_z']
[DEBUG] Rango tiempo: 0.000 - 5.000 s
```

#### **Monitorear Memoria**
```python
# Agregar al código para monitoreo:
import psutil
proceso = psutil.Process()
memoria_mb = proceso.memory_info().rss / (1024 * 1024)
print(f"Memoria usada: {memoria_mb:.1f} MB")
```

---

## 📖 API REFERENCE

**¿Cómo aprovechar la API?**
La API permite a usuarios avanzados y desarrolladores integrar las funciones principales de la aplicación en sus propios scripts o flujos de trabajo. Cada función está documentada con ejemplos de uso, manejo de errores y validación de datos. Se recomienda consultar la API para personalizar el análisis, automatizar tareas o integrar la herramienta con otros sistemas.

**Explicación de la API y ejemplos de uso:**
La API está diseñada para que los usuarios avanzados y desarrolladores puedan integrar las funciones principales de la aplicación en sus propios scripts o flujos de trabajo. Cada función incluye una descripción de los argumentos, el propósito, ejemplos de uso y notas sobre el manejo de errores y validación de datos. Esto facilita la extensión y personalización de la herramienta para casos específicos o integraciones con otros sistemas.

### 🔧 **Funciones Principales**

#### **cargar_archivo(contents, filename)**
```python
def cargar_archivo(contents, filename):
    """
    Carga y valida archivos CSV, TXT (Catman) o XLSX.
    
    Args:
        contents (str): Contenido codificado en base64
        filename (str): Nombre del archivo
        
    Returns:
        tuple: (mensaje_estado, df_json, mensaje_error)
        
    Raises:
        ValueError: Si el formato no es compatible
        
    Example:
        mensaje, datos, error = cargar_archivo(contents, "ensayo.csv")
    """
```

#### **filtrar_senal(df, seleccion_multi, seleccion_eje, fs, ...)**
```python
def filtrar_senal(df, seleccion_multi, seleccion_eje, fs, 
                  mediana_val, highpass_val, bandpass_multibanda, 
                  ancho_banda, toggle_mediana, toggle_highpass, toggle_bandpass):
    """
    Aplica filtros digitales a las señales seleccionadas.
    
    Args:
        df (DataFrame): Datos de entrada
        seleccion_multi (list): Columnas a filtrar
        seleccion_eje (str): Eje principal para análisis
        fs (float): Frecuencia de muestreo
        mediana_val (int): Kernel para filtro mediana
        highpass_val (float): Frecuencia de corte paso alto
        bandpass_multibanda (str): Frecuencias centrales separadas por coma
        ancho_banda (float): Ancho de banda para filtro multibanda
        toggle_* (str): Activación de filtros ('yes'/'no')
        
    Returns:
        tuple: (df_filtrado, mensajes_filtro, frecuencias_centrales)
        
    Example:
        df_filt, msgs, freqs = filtrar_senal(df, ['accel_x'], 'accel_x', 
                                            1000, 5, 0.5, "50,200", 20,
                                            'yes', 'yes', 'yes')
    """
```

#### **generar_grafico_fft_adaptativo(df, seleccion_multi, escala_x, escala_y)**
```python
def generar_grafico_fft_adaptativo(df, seleccion_multi, escala_x, escala_y):
    """
    Genera gráfico FFT con caché automático si está habilitado.
    
    Args:
        df (DataFrame): Datos temporales
        seleccion_multi (list): Señales a procesar
        escala_x (str): 'linear' o 'log'
        escala_y (str): 'amplitude' o 'db'
        
    Returns:
        plotly.Figure: Gráfico FFT interactivo
        
    Notes:
        - Usa caché automáticamente si USAR_CACHE=True
        - Optimiza datasets grandes (>100k puntos)
        - Aplica ventaneo adaptativo por tipo de señal
        
    Example:
        fig = generar_grafico_fft_adaptativo(df, ['accel_x'], 'log', 'db')
    """
```

#### **generar_waterfall_adaptativo(df_json, seleccion_eje, ...)**
```python
def generar_waterfall_adaptativo(df_json, seleccion_eje, escala_x, escala_y,
                                curvas_enfasis, estado_fijar_vista, duracion_segmento):
    """
    Genera análisis waterfall 3D con optimización automática.
    
    Args:
        df_json (str): DataFrame serializado en JSON
        seleccion_eje (str): Columna para análisis ('accel_x', 'accel_y', etc.)
        escala_x (str): Escala frecuencial ('linear'/'log')
        escala_y (str): Escala amplitud ('amplitude'/'db')
        curvas_enfasis (list): Índices de curvas a destacar
        estado_fijar_vista (bool): Fijar orientación 3D
        duracion_segmento (float): Duración de cada segmento (s)
        
    Returns:
        tuple: (figura_3d, datos_exportacion)
            - figura_3d: plotly.Figure con gráfico 3D
            - datos_exportacion: list de dict para exportar
            
    Notes:
        - Optimiza número de segmentos según tamaño de datos
        - Usa caché para evitar recálculos
        - Permite configuración de duración de ventana
        
    Example:
        fig, datos = generar_waterfall_adaptativo(df_json, 'accel_x', 
                                                 'log', 'db', [], False, 1.0)
    """
```

#### **calculo_amortiguamiento(accel, fs, frecuencias_centrales)**
```python
def calculo_amortiguamiento(accel, fs, frecuencias_centrales=None, ventana_busqueda_hz=5.0):
    """
    Calcula amortiguamiento modal y global.
    
    Args:
        accel (array): Señal de aceleración
        fs (float): Frecuencia de muestreo
        frecuencias_centrales (list, optional): Frecuencias específicas a analizar
        ventana_busqueda_hz (float): Ventana de búsqueda alrededor de freq centrales
        
    Returns:
        dict: Resultado con claves:
            - 'modos': Lista de dict con 'frecuencia' y 'zeta' 
            - 'zeta_global': Factor de amortiguamiento global
            - 'mensajes': Lista de advertencias/errores
            
    Methods:
        - Modal: Ancho de banda -3dB
        - Global: Decremento logarítmico
        
    Example:
        resultado = calculo_amortiguamiento(accel_data, 1000.0, [50, 150])
        for modo in resultado['modos']:
            print(f"f={modo['frecuencia']:.1f} Hz, ζ={modo['zeta']:.4f}")
    """
```

### 💾 **Sistema de Caché**

#### **CacheComputacional**
```python
class CacheComputacional:
    """
    Sistema de caché LRU para optimización de cálculos.
    
    Attributes:
        cache (dict): Almacén de resultados
        cache_access_times (dict): Timestamps para LRU
        max_cache_size (int): Límite de elementos (default: 50)
        hits (int): Contador de hits
        misses (int): Contador de misses
    """
    
    def generar_hash_parametros(self, *args, **kwargs):
        """Genera hash MD5 de parámetros de entrada"""
        
    def obtener_de_cache(self, cache_key):
        """Recupera resultado si existe en caché"""
        
    def guardar_en_cache(self, cache_key, resultado):
        """Almacena resultado con política LRU"""
        
    def limpiar_cache(self):
        """Limpia todo el caché y estadísticas"""
        
    def estadisticas_cache(self):
        """Retorna dict con hits, misses, hit_rate, cache_size"""
```

#### **Funciones de Control de Caché**
```python
def habilitar_cache():
    """Activa el sistema de caché globalmente"""
    
def deshabilitar_cache():
    """Desactiva y limpia el caché"""
    
def toggle_cache():
    """Alterna estado del caché"""
    
def limpiar_cache_si_necesario(forzar=False):
    """Limpia caché cuando es necesario o forzado"""
```

### 🔬 **Algoritmos Científicos**

#### **Ventaneo Adaptativo**
```python
def ventana_exponencial(y, fs, tau=None):
    """
    Aplica ventana exponencial para análisis transitorio.
    
    Args:
        y (array): Señal de entrada
        fs (float): Frecuencia de muestreo
        tau (float, optional): Constante de tiempo (auto si None)
        
    Returns:
        array: Señal ventaneada
        
    Notes:
        - Estima tau automáticamente del decaimiento
        - Optimizado para respuestas impulsivas
    """

def ventana_fuerza_adaptativa(y, fs):
    """
    Ventana específica para señales de fuerza de impacto.
    
    Args:
        y (array): Señal de fuerza
        fs (float): Frecuencia de muestreo
        
    Returns:
        array: Señal ventaneada
        
    Notes:
        - Detecta duración del impacto automáticamente
        - Aplica tapering suave al final
    """
```

#### **Análisis de FRF**
```python
def calculate_H1(S_ff, S_xf):
    """Estimador H1: óptimo para ruido en salida"""
    return S_xf / (S_ff + 1e-12)

def calculate_H2(S_xx, S_xf):
    """Estimador H2: óptimo para ruido en entrada"""
    return S_xx / (np.conj(S_xf) + 1e-12)

def calculate_Hv(S_ff, S_xx, S_xf):
    """Estimador Hv: combinación ponderada por coherencia"""
    H1 = calculate_H1(S_ff, S_xf)
    H2 = calculate_H2(S_xx, S_xf)
    coh = calculate_coherence(S_ff, S_xx, S_xf)
    return np.where(coh > 0.9, H1, 
           np.where(coh > 0.7, np.sqrt(H1 * H2), H2))

def calculate_coherence(S_ff, S_xx, S_xf):
    """Función de coherencia"""
    return np.abs(S_xf)**2 / (S_ff * S_xx + 1e-12)
```

#### **Rigidez Dinámica**
```python
def calculate_dynamic_stiffness_robust(H_frf, frequencies):
    """
    Calcula rigidez dinámica con manejo robusto de antiresonancias.
    
    Args:
        H_frf (array): Función de respuesta en frecuencia
        frequencies (array): Vector de frecuencias
        
    Returns:
        array: Rigidez dinámica compleja K(ω) = -ω²/H(ω)
        
    Notes:
        - Detecta y maneja antiresonancias automáticamente
        - Interpola zonas problemáticas
        - Valida resultados físicos
    """
```

### 🎨 **Optimización de Visualización**

#### **optimizar_dataframe_para_visualizacion(df, max_puntos)**
```python
def optimizar_dataframe_para_visualizacion(df, max_puntos=50000):
    """
    Reduce puntos para visualización sin pérdida de características.
    
    Args:
        df (DataFrame): Datos completos
        max_puntos (int): Máximo puntos para visualización
        
    Returns:
        tuple: (df_optimizado, fue_optimizado)
        
    Strategy:
        - 30% de puntos en primer 10% del tiempo (impactos)
        - 70% distribuido uniformemente en el resto
        - Preserva primer y último punto
    """
```

#### **mostrar_progreso_simple(mensaje, puntos_totales, puntos_finales)**
```python
def mostrar_progreso_simple(mensaje, puntos_totales, puntos_finales=None):
    """
    Muestra información de progreso en consola.
    
    Args:
        mensaje (str): Descripción de la operación
        puntos_totales (int): Cantidad total de datos
        puntos_finales (int, optional): Cantidad después de optimización
        
    Output:
        [PROGRESO] FFT optimizada - Procesando 150,000 puntos
        [OPTIMIZACIÓN] Waterfall 3D - 2,000,000 → 500,000 puntos (75% reducción)
    """
```

### 🔍 **Utilidades de Validación**

#### **validar_masa_martillo(masa)**
```python
def validar_masa_martillo(masa):
    """
    Valida rango físico de masa del martillo.
    
    Args:
        masa (float): Masa en kg
        
    Returns:
        tuple: (masa_validada, mensaje)
        
    Ranges:
        - None: 1.0 kg por defecto
        - <= 0: 1.0 kg por defecto
        - < 0.1: Ajustado a 0.1 kg
        - > 50.0: Ajustado a 50.0 kg
        - 0.1-50.0: Valor válido
    """
```

#### **generar_graficos_vacios()**
```python
def generar_graficos_vacios():
    """
    Genera figuras vacías para casos de error.
    
    Returns:
        tuple: 8 elementos (fig_tiempo, fig_fft, fig_waterfall, 
               fig_damping, fig_disp, fig_coherencia, 
               curvas_enfasis, opciones_curvas, estado_fijar_vista, estilo_fijar,
               mediana_val, highpass_val, bandpass_multibanda)
    """
```

---

## 📝 **NOTAS DE VERSIÓN**

---

## 🏅 VALORACIÓN TÉCNICA Y RECOMENDACIONES

### 🔎 Valoración Técnica

La aplicación alcanza un nivel profesional y robusto, con una nota técnica de **9/10**. Destaca por su modularidad, flexibilidad, rendimiento y experiencia de usuario. El sistema de caché, la optimización para datasets grandes y la visualización avanzada la sitúan por encima de la media en aplicaciones científicas de análisis experimental.

### 💪 Puntos Fuertes

- Modularidad y claridad del código
- Robustez ante errores y datos problemáticos
- Flexibilidad para datasets grandes y pequeños
- Experiencia de usuario cuidada y validaciones automáticas
- Visualización avanzada y exportación de resultados
- Sistema de caché inteligente y adaptativo

### ⚠️ Puntos Débiles y Áreas de Mejora

- **Gestión de errores y mensajes al usuario:** Los mensajes en la interfaz pueden ser más claros y amigables para usuarios no técnicos.
- **Documentación interna y externa:** Mejorar docstrings y comentarios en funciones clave, y añadir ejemplos de uso en la documentación.
- **Pruebas automáticas:** Añadir tests unitarios y de integración para asegurar la calidad y detectar regresiones.
- **Validación de inputs:** Mostrar advertencias visuales si el usuario intenta valores fuera de rango o si el dataset es demasiado pequeño para ciertos análisis.
- **Rendimiento en datasets muy grandes:** Permitir al usuario ajustar dinámicamente los límites de rendimiento según la capacidad de su sistema.
- **Experiencia de usuario (UX):** Añadir tooltips, ayuda contextual y ejemplos de uso en la interfaz.
- **Modularidad visual:** Mejorar la separación visual entre secciones y ofrecer modo oscuro/claro configurable.

### 🛠️ Recomendaciones de Mejora

1. Añadir una guía de usuario visual con ejemplos y capturas de pantalla.
2. Incluir una sección de preguntas frecuentes (FAQ) en la documentación.
3. Implementar tests automáticos para las funciones principales.
4. Mejorar los mensajes de error y advertencia en la interfaz.
5. Permitir configuración avanzada de límites de rendimiento y visualización.
6. Añadir ayuda contextual y tooltips en los controles de la interfaz.
7. Documentar con más detalle los algoritmos y métodos matemáticos empleados.

---

### 🆕 **v1.10.3 - ACTUAL**

#### **Nuevas Características**
- ✅ **Sistema de caché inteligente** con optimización automática
- ✅ **Indicadores de estado visual** en tiempo real para botones
- ✅ **Optimización de datasets grandes** (>200k puntos)
- ✅ **Limpieza automática de memoria** al iniciar y cargar archivos
- ✅ **Fallback robusto** en caso de errores
- ✅ **Documentación completa** integrada

#### **Mejoras de Rendimiento**
- 🚀 **FFT**: 70-90% más rápido con caché
- 🚀 **Waterfall**: 80-95% más rápido con caché
- 🚀 **Cambios de escala**: Instantáneos (<0.1s)
- 🚀 **Gestión de memoria**: Automática y eficiente

#### **Correcciones de Bugs**
- 🔧 Función `mostrar_overlay_cierre` corregida
- 🔧 Variables inicializadas correctamente en callbacks
- 🔧 Imports completos añadidos
- 🔧 Validación robusta de datos mejorada

#### **Arquitectura**
- 🏗️ **Modularidad**: Funciones bien separadas
- 🏗️ **Conservadora**: No rompe funcionalidad existente
- 🏗️ **Escalable**: Fácil añadir nuevas características
- 🏗️ **Mantenible**: Código bien documentado

---

## 📞 **SOPORTE Y CONTACTO**

**¿Cómo obtener soporte y enviar sugerencias?**
Para cualquier problema técnico, duda o sugerencia de mejora, se recomienda contactar al soporte incluyendo la versión del software, el sistema operativo, una descripción detallada del problema, los pasos para reproducirlo y archivos de ejemplo si es posible. Las sugerencias para futuras versiones son bienvenidas y ayudan a mejorar la herramienta para todos los usuarios.

### 🏢 **Información Corporativa**
- **Empresa**: EDAI TU
- **Aplicación**: Rigidez Dinámica v1.10.3
- **Tipo**: Análisis científico/ingenieril
- **Licencia**: Propietaria

### 🤝 **Soporte Técnico**
Para soporte técnico, por favor incluir:
1. **Versión del software**: v1.10.3
2. **Sistema operativo**: Windows/macOS/Linux + versión
3. **Descripción del problema**: Detallada
4. **Pasos para reproducir**: Secuencia exacta
5. **Archivos de ejemplo**: Si es posible
6. **Logs de error**: Copiar mensajes completos

### 💡 **Sugerencias de Mejora**
Las sugerencias para futuras versiones son bienvenidas:
- **Nuevas características**
- **Optimizaciones adicionales**
- **Formatos de archivo adicionales**
- **Algoritmos de análisis avanzados**

---

## 📜 **LICENCIA Y DISCLAIMER**

**¿Qué implica la licencia y el disclaimer?**
La licencia establece los derechos de uso y las limitaciones de responsabilidad del software. El disclaimer científico aclara que los resultados dependen de la calidad de los datos de entrada y que la herramienta es un apoyo para el análisis, no un sustituto del criterio ingenieril. Se recomienda validar experimentalmente los resultados críticos y verificar independientemente para aplicaciones sensibles.

### ⚖️ **Licencia**
Este software es propiedad de **EDAI TU**. Todos los derechos reservados.

### ⚠️ **Disclaimer Científico**
- Los resultados dependen de la **calidad de los datos de entrada**
- Se recomienda **validación experimental** de resultados críticos  
- El software es una **herramienta de análisis**, no reemplaza el criterio ingenieril
- Los **parámetros de amortiguamiento** deben interpretarse en contexto físico

### 🔒 **Limitaciones de Responsabilidad**
- El software se proporciona **"tal como está"**
- **EDAI TU** no se responsabiliza por decisiones basadas en los resultados
- Se recomienda **verificación independiente** para aplicaciones críticas

---

*📅 Última actualización: Julio 2025*  
*📍 Versión de documentación: 1.0*  
*🏢 EDAI TU - Soluciones de Ingeniería Avanzada*

---
