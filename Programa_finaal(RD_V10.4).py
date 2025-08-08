import base64
from datetime import datetime
import dash
from functools import lru_cache
import gc
import hashlib
import io
import numpy as np
import os
import pandas as pd
import pickle
import plotly.graph_objects as go
import tempfile
import threading
import time
import traceback
import re
import webbrowser
import zipfile
from dash import dash_table, Dash, html, dcc, callback, Output, Input, State, ctx, no_update
from plotly.subplots import make_subplots
from scipy.fft import rfft, rfftfreq
from scipy.signal import get_window, welch, csd, find_peaks, medfilt, butter, filtfilt, firwin, periodogram, sosfiltfilt
from scipy.stats import median_abs_deviation
from dynamic_stiffness_analyzer.visualization.shared import (
    generar_graficos_vacios,
    generar_figura_vacia,
)

# Intento de usar configuración modular externa; si falla, se usarán las definiciones locales
try:
    from dynamic_stiffness_analyzer.config.settings import CONFIG as CONFIG_EXT, USAR_CACHE as USAR_CACHE_EXT  # type: ignore
    CONFIG = CONFIG_EXT
    USAR_CACHE = USAR_CACHE_EXT
except Exception:
    # La configuración local definida más abajo seguirá activa
    pass

app = Dash()

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                            # --- Configuración del sistema de caché ---

# Asignación segura por defecto solo si no existe USAR_CACHE (evita sobreescribir import externo)
try:
    USAR_CACHE
except NameError:
    USAR_CACHE = False  # DESHABILITADO TEMPORALMENTE para aplicar correcciones de frecuencias

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                    # --- Configuración de parámetros ---

class ConfiguracionSistema:
    """
    - Configuración centralizada de parámetros hardcodeados del sistema.
    - NOTA: Las optimizaciones del 75% (tau=0.7, factor_ruido=2, etc.) NO están aquí porque son configuraciones específicas
           y justificadas.
    """
    
    # Límites de visualización
    VISUALIZACION = {'MAX_PUNTOS_TIEMPO': 20000,      # Reducir puntos para gráfico tiempo si excede
                     'MAX_PUNTOS_FFT': 50000,         # Reducir puntos para gráfico FFT si excede
                     'REDUCCION_VISUAL_FFT': 20000,   # Objetivo de puntos tras reducción
                     'MAX_SEGMENTOS_WATERFALL': 120,  # Máximo segmentos en waterfall 3D
                    }
    
    # Tamaños de ventana para waterfall
    VENTANAS_WATERFALL = {'GRANDE': 4096,    # Para datasets > 100k puntos
                          'MEDIO': 2048,     # Para datasets > 50k puntos  
                          'PEQUEÑO': 1024,   # Para datasets normales
                          'MINIMO': 512,     # Ventana mínima absoluta
                         }
    
    # Umbrales de datos
    UMBRALES_DATOS = {'DATASET_GRANDE': 100000,     # Puntos para considerar dataset grande
                      'DATASET_MEDIO': 50000,       # Puntos para considerar dataset medio
                      'MIN_SEGMENTOS_WELCH': 6,     # Mínimo segmentos para análisis Welch
                      'MIN_PUNTOS_SEGMENTO': 256,   # Mínimo puntos por segmento
                      'MAX_PUNTOS_SEGMENTO': 1024,  # Máximo puntos por segmento
                      'MAX_SEGMENTOS': 120,         # Máximo segmentos waterfall para rendimiento
                      'MIN_AMPLITUD_RUIDO': 1e-8,   # Amplitud mínima considerada señal
                      'FACTOR_UMBRAL_SFF': 0.01,    # 1% del máximo para Sff
                     }
    
    # validación física
    LIMITES_FISICOS = {'MASA_MIN': 0.1,       # kg - Masa mínima martillo
                       'MASA_MAX': 50.0,      # kg - Masa máxima martillo
                       'FREQ_MIN': 0.1,       # Hz - Frecuencia mínima válida
                       'DT_MIN': 1e-6,        # s - dt mínimo válido
                       'DT_MAX': 1.0,         # s - dt máximo válido
                      }
    
    # Tolerancias numericas
    TOLERANCIAS = {'IRREGULARIDAD_TEMPORAL': 0.05,   # 5% - Umbral para regenerar tiempo
                   'EPSILON_DIVISION': 1e-12,        # Evitar división por cero
                   'MIN_COHERENCIA_VALIDA': 1e-10,   # Coherencia mínima considerada válida
                   'MIN_DURACION_SEGMENTO': 0.05,    # 50ms - Duración mínima de segmento
                   'DECAY_THRESHOLD': 0.05,          # 5% amplitud - Umbral decaimiento señal
                   'THRESHOLD_FACTOR': 0.1,          # 10% - Factor umbral ventana impacto
                   'MAX_VENTANA_IMPACTO': 0.05,      # 50ms - Ventana máxima impacto
                   'MIN_VENTANA_IMPACTO': 0.0005,    # 0.5ms - Ventana mínima impacto
                   'MARGEN_GRAFICO': 0.05,           # 5% margen extra en ejes Y
                  }

# Instancia global de configuración
CONFIG = ConfiguracionSistema()

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                            # --- Configuración del sistema de caché ---

# Evitar duplicar/forzar el valor si ya existe de import externo
try:
    USAR_CACHE
except NameError:
    USAR_CACHE = False  # DESHABILITADO TEMPORALMENTE para aplicar correcciones de frecuencias

# --- Activación automática de caché según tamaño de datos ---
def evaluar_cache_por_tamano(df):
    
    #Activa o desactiva el caché automáticamente si el dataset es grande.
    global USAR_CACHE
    try:
        if df is not None and hasattr(df, '__len__') and len(df) > CONFIG.UMBRALES_DATOS['DATASET_GRANDE']:
            if not USAR_CACHE:
                habilitar_cache()
                print(f"[CACHE] Activado automáticamente por tamaño de datos: {len(df)} puntos")
        else:
            if USAR_CACHE:
                deshabilitar_cache()
                print(f"[CACHE] Desactivado automáticamente por tamaño de datos: {len(df) if df is not None else 0} puntos")
    except Exception as e:
        print(f"[CACHE] Error en evaluación automática: {e}")

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                            # --- Desactivar caché en el navegador ---

@app.server.after_request

def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                                # --- Layout completo ---

app.layout = html.Div([dcc.Store(id='store-df'), dcc.Store(id='store-df-corte'), dcc.Store(id='store-df-filtrado'),
                       html.Div([
                           html.Div([
                               html.H1('Rigidez Dinámica', style={'color': 'white',
                                                                  'flex': '1',
                                                                  'margin': 0,
                                                                  'padding': 0}),
                               html.Img(src='assets/logo_edai.png', style={'height': '70px',
                                                                           'marginLeft': '25px',
                                                                           'marginRight': '5px', }),
                           ], style={'display': 'flex',
                                     'flexDirection': 'row',
                                     'alignItems': 'center'}),
                           html.Button('Cerrar aplicación', id='boton-cerrar-app', n_clicks=0, style={'marginLeft': 'auto',
                                                                                                      'backgroundColor': '#dc3545',
                                                                                                      'color': 'white',
                                                                                                      'fontWeight': 'bold',
                                                                                                      'borderRadius': '4px',
                                                                                                      'border': 'none',
                                                                                                      'padding': '8px 15px',
                                                                                                      'height': '40px',
                                                                                                      'alignSelf': 'center'}),
                                ], style={'display': 'flex',
                                          'flexDirection': 'row',
                                          'alignItems': 'center',
                                          'justifyContent': 'space-between',
                                          'marginBottom': '10px'}),
                       html.Div(id='mensaje-cierre', style={'color': 'red',
                                                            'fontWeight': 'bold',
                                                            'fontSize': '18px',
                                                            'marginTop': '10px',
                                                            'marginBottom': '10px',
                                                            'textAlign': 'right'}),
                       dcc.Store(id='estado-cierre', data=False),
                       html.Div(id='overlay-cierre'),

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                                    # --- Carga de archivo ---

                       html.Div([
                           html.Label('Cargar archivo CSV de datos:', style={'color': 'white',
                                                                             'marginRight': '10px'}),
                           dcc.Upload(id='upload-data',
                                      children=html.Button('Seleccionar archivo', style={'backgroundColor': '#444',
                                                                                         'color': 'white',
                                                                                         'fontWeight': 'bold',
                                                                                         'borderRadius': '4px',
                                                                                         'border': 'none',
                                                                                         'padding': '8px 15px'}),
                                      multiple=False),
                           html.Div(id='nombre-archivo', style={'color': 'white',
                                                                'marginLeft': '15px'}),
                           dcc.Loading(id='loading-carga', type='circle', color='#28a745',
                                       children=[
                                           html.Div(id='mensaje-cargando', style={'color': 'white',
                                                                                  'marginLeft': '15px'})])
                                ], style={'display': 'flex',
                                          'flexDirection': 'row',
                                          'alignItems': 'center',
                                          'marginBottom': '20px'}),

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                                    # --- Parámetros del ensayo ---

                       html.Div([
                           html.H3('Parámetros del ensayo', style={'color': 'white',
                                                                   'marginBottom': '10px'}),
                           html.Div([
                               html.Label('Masa martillo:', style={'color': 'white',
                                                                   'marginRight': '5px',
                                                                   'fontWeight': 'bold'}),
                               dcc.Input(id='input-masa-martillo', type='number', value=1.0, 
                                         min=CONFIG.LIMITES_FISICOS['MASA_MIN'], max=CONFIG.LIMITES_FISICOS['MASA_MAX'],
                                         step=0.1, placeholder='1.0', style={'width': '70px'}),
                               html.Span('kg', style={'color': 'white',
                                                      'marginLeft': '3px',
                                                      'marginRight': '15px'}),
                               html.Button([
                                   html.Span('✓', id='icono-masa', style={'marginRight': '5px',
                                                                           'fontSize': '16px'}),
                                   'Aplicar masa'], id='boton-aplicar-masa', n_clicks=0, disabled=True, style={'backgroundColor': '#6c757d',
                                                                                                               'color': 'white',
                                                                                                               'fontWeight': 'bold',
                                                                                                               'borderRadius': '4px',
                                                                                                               'border': 'none',
                                                                                                               'padding': '8px 15px',
                                                                                                               'marginRight': '15px'}),
                               html.Div(id='mensaje-masa-martillo', style={'color': 'lightgreen',
                                                                           'fontSize': '14px',
                                                                           'fontWeight': 'bold'})
                                    ], style={'display': 'flex',
                                              'alignItems': 'center'}),
                                ], style={'backgroundColor': '#222',
                                          'padding': '10px',
                                          'borderRadius': '8px',
                                          'marginBottom': '20px'}),

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                                    # --- Controles de filtros ---

                       html.Div([
                           html.H3('Filtros de señal', style={'color': 'white',
                                                              'marginBottom': '10px'}),

                           # Todos los filtros en una sola línea
                           html.Div([

                               # Filtro mediana
                               html.Div([
                                   html.Label('Mediana:', style={'color': 'white',
                                                                 'marginRight': '5px',
                                                                 'fontWeight': 'bold'}),
                                   dcc.RadioItems(id='toggle-mediana', options=[{'label': 'Sí', 'value': 'yes'},
                                                                                {'label': 'No', 'value': 'no'}],
                                                  value='yes',
                                                  labelStyle={'display': 'inline-block',
                                                              'marginRight': '5px',
                                                              'color': 'white'}),
                                   dcc.Input(id='input-mediana', type='number', placeholder='5',
                                             style={'width': '50px'}), ], style={'display': 'flex',
                                                                                 'alignItems': 'center',
                                                                                 'marginRight': '20px'}),

                               # Filtro paso alto
                               html.Div([
                                   html.Label('Paso alto:', style={'color': 'white',
                                                                   'marginRight': '5px',
                                                                   'fontWeight': 'bold'}),
                                   dcc.RadioItems(id='toggle-highpass', options=[{'label': 'Sí', 'value': 'yes'},
                                                                                 {'label': 'No', 'value': 'no'}],
                                                  value='yes',
                                                  labelStyle={'display': 'inline-block',
                                                              'marginRight': '5px',
                                                              'color': 'white'}),
                                   dcc.Input(id='input-highpass', type='number', placeholder='0.5', style={'width': '60px'}),
                                   html.Span('Hz', style={'color': 'white',
                                                          'marginLeft': '3px'}), ], style={'display': 'flex',
                                                                                           'alignItems': 'center',
                                                                                           'marginRight': '20px'}),

                               # Filtro multibanda
                               html.Div([
                                   html.Label('Multibanda:', style={'color': 'white',
                                                                    'marginRight': '5px',
                                                                    'fontWeight': 'bold'}),
                                   dcc.RadioItems(id='toggle-bandpass', options=[{'label': 'Sí', 'value': 'yes'},
                                                                                 {'label': 'No', 'value': 'no'}],
                                                  value='yes', labelStyle={'display': 'inline-block',
                                                                           'marginRight': '5px',
                                                                           'color': 'white'}),
                                   dcc.Input(id='input-bandpass-multibanda', type='text', placeholder='50,200',
                                             style={'width': '140px',
                                                    'marginRight': '5px'}),
                                   html.Span('Hz', style={'color': 'white'}), ], style={'display': 'flex',
                                                                                        'alignItems': 'center',
                                                                                        'marginRight': '20px'}),

                               # Botón aplicar filtros
                               html.Button([
                                   html.Span('✓', id='icono-filtros', style={'marginRight': '5px', 'fontSize': '16px'}),
                                             'Aplicar filtros'
                                           ], id='boton-aplicar-filtros', n_clicks=0, disabled=True, style={'backgroundColor': '#6c757d',
                                                                                                            'color': 'white',
                                                                                                            'fontWeight': 'bold',
                                                                                                            'borderRadius': '4px',
                                                                                                            'border': 'none',
                                                                                                            'padding': '8px 15px',
                                                                                                            'marginRight': '15px'}),

                               # Mensaje de filtros
                               html.Div(id='mensaje-filtro', style={'color': 'orange',
                                                                    'fontWeight': 'bold',
                                                                    'fontSize': '14px'}), ], style={'display': 'flex',
                                                                                                    'flexWrap': 'wrap',
                                                                                                    'alignItems': 'center',
                                                                                                    'marginBottom': '10px'}), ],
                                        style={'backgroundColor': '#222',
                                               'padding': '10px',
                                               'borderRadius': '8px',
                                               'marginBottom': '20px'}),

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                                # --- Controles de corte de señal ---

                       html.Div([
                           html.H3('Corte de señal por tiempo', style={'color': 'white'}),
                           html.Div([
                               html.Label('Inicio (s):', style={'color': 'white',
                                                                'marginRight': '5px'}),
                               dcc.Input(id='input-corte-inicio', type='number', placeholder='Tiempo inicio (s)',
                                         style={'width': '120px',
                                                'marginRight': '20px'}),

                               html.Label('Fin (s):', style={'color': 'white',
                                                             'marginRight': '5px'}),
                               dcc.Input(id='input-corte-fin', type='number', placeholder='Tiempo fin (s)',
                                         style={'width': '120px',
                                                'marginRight': '20px'}),

                               html.Button([
                                   html.Span('✓', id='icono-corte', style={'marginRight': '5px', 'fontSize': '16px'}),
                                   'Aplicar corte'
                                           ], id='boton-aplicar-corte', n_clicks=0, disabled=True, style={'marginLeft': '30px',
                                                                                                          'backgroundColor': '#6c757d',
                                                                                                          'color': 'white',
                                                                                                          'fontWeight': 'bold',
                                                                                                          'borderRadius': '4px',
                                                                                                          'border': 'none',
                                                                                                          'padding': '8px 15px'}),
                               html.Div(id='mensaje-corte', style={'color': 'orange',
                                                                   'marginLeft': '20px',
                                                                   'fontWeight': 'bold',
                                                                   'fontSize': '16px'}),
                                    ], style={'display': 'flex',
                                              'flexDirection': 'row',
                                              'alignItems': 'center',
                                              'marginBottom': '10px'}),
                                ], style={'backgroundColor': '#222',
                                          'padding': '10px',
                                          'borderRadius': '8px',
                                          'marginBottom': '20px'}),

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                        # --- Controles de selección de señales y ejes ---

                       html.Div([
                           html.Div([
                               html.Label('Selecciona señales para tiempo / FFT:', style={'color': 'white'}),
                               dcc.Checklist(options=[{'label': 'Accel X', 'value': 'accel_x'},
                                                      {'label': 'Accel Y', 'value': 'accel_y'},
                                                      {'label': 'Accel Z', 'value': 'accel_z'},
                                                      {'label': 'Fuerza', 'value': 'fuerza'}],
                                             value=['accel_x'], id='selector-multi', style={'display': 'flex',
                                                                                            'flexDirection': 'column',
                                                                                            'color': 'white'}), ],
                               style={'marginRight': '30px'}),
                           html.Div([
                               html.Label('Selecciona eje para 3D y Rig. Dinamica:', style={'color': 'white'}),
                               dcc.RadioItems(options=[{'label': 'Accel X', 'value': 'accel_x'},
                                                       {'label': 'Accel Y', 'value': 'accel_y'},
                                                       {'label': 'Accel Z', 'value': 'accel_z'},
                                                       {'label': 'Fuerza', 'value': 'fuerza'}],
                                              value='accel_x', id='selector-eje', style={'display': 'flex',
                                                                                         'flexDirection': 'column',
                                                                                         'color': 'white'})
                           ], style={'marginRight': '30px'}), ], style={'display': 'flex',
                                                                        'flexDirection': 'row',
                                                                        'alignItems': 'flex-start',
                                                                        'marginBottom': '20px'}),

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                        # --- Controles de procesamiento y optimización ---

                       html.Div([
                           dcc.Store(id='procesamiento-estado', data={'activo': False, 'paso': 0, 'max_pasos': 5}),
                           dcc.Store(id='procesamiento-resultados', data={}),
                           dcc.Interval(id='procesamiento-interval', interval=100, n_intervals=0, disabled=True),
                           html.Div(id='progreso-procesamiento', style={'color': 'orange',
                                                                        'fontWeight': 'bold'}),
                           html.Button('Cancelar Procesamiento', id='cancelar-procesamiento',
                                       style={'backgroundColor': '#dc3545',
                                              'color': 'white',
                                              'display': 'none'})]),

##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
                                            # --- Callback para iniciar el procesamiento ---

                       dcc.Graph(id='grafico-tiempo'),
                       html.Div([
                           html.Div([
                               html.Label('Escala eje X (FFT y 3D):', style={'color': 'white',
                                                                             'marginRight': '20px'}),
                               dcc.RadioItems(options=[{'label': 'Lineal', 'value': 'linear'},
                                                       {'label': 'Logarítmico', 'value': 'log'}],
                                              value='linear', id='escala-x', style={'color': 'white',
                                                                                    'marginRight': '30px'}),
                               html.Label('Escala eje Y (Amplitud FFT y 3D):', style={'color': 'white',
                                                                                      'marginRight': '20px'}),
                               dcc.RadioItems(options=[{'label': 'Amplitud', 'value': 'amplitude'},
                                                       {'label': 'dB', 'value': 'db'}],
                                              value='amplitude', id='escala-y', style={'color': 'white',
                                                                                       'marginRight': '30px'}),
                                    ], style={'display': 'flex',
                                              'flexDirection': 'row',
                                              'alignItems': 'center',
                                              'marginBottom': '10px',
                                              'minWidth': '200px'}),
                           dcc.Graph(id='grafico-fft'), ], style={'width': '100%',
                                                                  'marginBottom': '40px'}),
                       html.Div([
                           html.Label("Selecciona curvas:", style={'color': 'white'}),
                           dcc.Dropdown(id='selector-curvas', options=[], value=[], multi=True,
                                        placeholder="Selecciona curvas...", style={'marginBottom': '10px'}),
                           html.Div([
                               html.Button("Restablecer visibilidad", id='boton-reset', n_clicks=0,
                                           style={'marginRight': '10px',
                                                  'backgroundColor': '#444',
                                                  'color': 'white',
                                                  'fontWeight': 'bold',
                                                  'borderRadius': '4px',
                                                  'border': 'none',
                                                  'padding': '8px 15px'}),
                               dcc.Store(id='estilo-fijar-vista', data={'backgroundColor': '#7C8085',
                                                                        'color': 'white',
                                                                        'fontWeight': 'bold',
                                                                        'borderRadius': '4px',
                                                                        'border': 'none',
                                                                        'padding': '8px 15px'}),
                               html.Button("Fijar vista", id='boton-fijar-vista', n_clicks=0,
                                           style={'backgroundColor': '#7C8085',
                                                  'color': 'white',
                                                  'fontWeight': 'bold',
                                                  'borderRadius': '4px',
                                                  'border': 'none',
                                                  'padding': '8px 15px'},
                                           ),
                               html.Label('Duración de segmento 3D (s):', style={'color': 'white',
                                                                                 'marginLeft': '30px',
                                                                                 'marginRight': '5px'}),
                               dcc.Input(id='input-duracion-segmento', type='number', 
                                         min=CONFIG.TOLERANCIAS['MIN_DURACION_SEGMENTO'], max=9999, step=0.01,
                                         value=1.0, style={'width': '80px'}),
                               html.Button('Aplicar duración segmento', id='boton-aplicar-duracion-segmento',
                                           n_clicks=0, style={'marginLeft': '10px',
                                                              'backgroundColor': '#28a745',
                                                              'color': 'white',
                                                              'fontWeight': 'bold',
                                                              'borderRadius': '4px',
                                                              'border': 'none',
                                                              'padding': '8px 15px'}),
                               html.Span(id='texto-rango-duracion-segmento', style={'color': 'orange',
                                                                                    'marginLeft': '10px'}),
                                    ], style={'display': 'flex',
                                              'flexDirection': 'row',
                                              'alignItems': 'center',
                                              'marginBottom': '10px'}),
                           dcc.Graph(id='grafico-waterfall', style={'width': '100%',
                                                                    'height': '800px'}),
                           html.Button('Exportar datos 3D', id='boton-exportar-waterfall', n_clicks=0, style={'marginTop': '10px',
                                                                                                              'backgroundColor': '#007bff',
                                                                                                              'color': 'white',
                                                                                                              'fontWeight': 'bold',
                                                                                                              'borderRadius': '4px',
                                                                                                              'border': 'none',
                                                                                                              'padding': '8px 15px'}),
                           dcc.Download(id='descarga-waterfall'),
                           html.Div(id='amortiguamiento-tables', style={'width': '100%',
                                                                        'marginTop': '30px'}),
                           dcc.Graph(id='grafico-desplazamiento', style={'width': '100%',
                                                                         'height': '400px',
                                                                         'marginTop': '30px'}),
                           html.Div(style={'height': '150px'}),

                           # Espacio extra entre desplazamiento/fase y coherencia para evitar superposición
                           dcc.Graph(id='grafico-coherencia', style={'width': '100%',
                                                                     'height': '300px',
                                                                     'marginTop': '30px'}),
                           dcc.Store(id='estado-fijar-vista', data=False),], style={'width': '100%'}), ], style={'backgroundColor': '#111111',
                                                                                                                 'padding': '20px'})

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                    # --- Callback y funcion para activar el pantalla de cierre ---

@callback(Output('estado-cierre', 'data'),
          Input('boton-cerrar-app', 'n_clicks'),
          prevent_initial_call=True
         )

def activar_cierre(n_clicks):
    if n_clicks:
        return True
    return no_update

#######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                # --- Callback y funcion para mostrar el la pantalla de cierre y agradecimiento ---

@callback(Output('overlay-cierre', 'children'),
          Input('estado-cierre', 'data')
         )

def mostrar_overlay_cierre(estado):
    if estado:
        return html.Div(
            [
                html.Div([
                    html.H2("La aplicación se cerrará en un momento...", style={'marginBottom': '20px'}),
                    html.H3("¡Gracias por usar la aplicación!", style={'fontWeight': 'normal'}),
                    html.H4("Propiedad de EDAI TU", style={'fontWeight': 'normal'})
                         ], style={'textAlign': 'center'})], style={'position': 'fixed',
                                                                    'top': 0,
                                                                    'left': 0,
                                                                    'width': '100vw',
                                                                    'height': '100vh',
                                                                    'backgroundColor': 'black',
                                                                    'color': 'white',
                                                                    'display': 'flex',
                                                                    'alignItems': 'center',
                                                                    'justifyContent': 'center',
                                                                    'flexDirection': 'column',
                                                                    'fontSize': '2em',
                                                                    'zIndex': 9999})
    return None

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                                # --- Callback para cerrar la aplicación ---

@callback(Output('mensaje-cierre', 'children'),
          Input('boton-cerrar-app', 'n_clicks'),
          prevent_initial_call=True
         )

def cerrar_aplicacion(n_clicks):
    if n_clicks:
        def cerrar():
            time.sleep(1.5)
            os._exit(0)
        threading.Thread(target=cerrar, daemon=True).start()
        return 'La aplicación se cerrará en un momento...'
    return ''

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                # --- Callback para mostrar el nombre del archivo cargado y mensaje de cargando ---

@callback(Output('nombre-archivo', 'children'),
          Output('store-df', 'data'),
          Output('mensaje-cargando', 'children'),
          Input('upload-data', 'contents'),
          State('upload-data', 'filename')
         )

def cargar_archivo(contents, filename):
    # Limpiar caché al cargar nuevo archivo para evitar inconsistencias
    if contents is not None and USAR_CACHE:
        cache_computacional.limpiar_cache()
        print("[CACHÉ] Caché limpiado al cargar nuevo archivo")

    try:
        from dynamic_stiffness_analyzer.io.loader import cargar_contenidos_upload
        msg, df_json, msg_loading = cargar_contenidos_upload(contents, filename)
        if df_json:
            try:
                df_tmp = pd.read_json(df_json, orient='split')
                evaluar_cache_por_tamano(df_tmp)
            except Exception:
                pass
        return msg, (df_json or ''), msg_loading
    except Exception as e:
        print(f"[ERROR] Error en loader modular: {e}")
        return 'Error al leer el archivo', '', ''

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                        # --- callback y funcion para exportar los datos del gráfico waterfall en ---

@callback(Output('descarga-waterfall', 'data'),
          Input('boton-exportar-waterfall', 'n_clicks'),
          prevent_initial_call=True
         )

def exportar_waterfall(n_clicks):
    datos = getattr(actualizar_graficos, 'datos_waterfall', None)
    if not datos:
        return None
    try:
        from dynamic_stiffness_analyzer.io.export import exportar_waterfall_a_zip
        zip_path = exportar_waterfall_a_zip(datos)
        if not zip_path:
            return None
        return dcc.send_file(zip_path, filename="datos_3D.zip")
    except Exception as e:
        print(f"[ERROR] Error en export modular: {e}")
        return None

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                    # --- Callback para deshabilitar los inputs de parámetros de filtros según el toggle correspondiente ---

@callback(Output('input-mediana', 'disabled'),
          Output('input-highpass', 'disabled'),
          Output('input-bandpass-multibanda', 'disabled'),
          Input('toggle-mediana', 'value'),
          Input('toggle-highpass', 'value'),
          Input('toggle-bandpass', 'value'),
         )

def deshabilitar_inputs_filtros(toggle_mediana, toggle_highpass, toggle_bandpass):
    return (toggle_mediana != 'yes',
            toggle_highpass != 'yes',
            toggle_bandpass != 'yes',
            )

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                    # --- Callback para aplicar filtros a los datos cargados ---

@app.callback(Output('input-duracion-segmento', 'min'),
              Output('input-duracion-segmento', 'max'),
              Input('store-df', 'data'),
              Input('store-df-corte', 'data'),
              Input('store-df-filtrado', 'data'),
             )

def actualizar_limites_duracion_segmento(df_json, df_corte_json, df_filtrado_json):
    min_val = CONFIG.TOLERANCIAS['MIN_DURACION_SEGMENTO']  # Mínimo fijo recomendado (50 ms)
    max_val = 9999  # Valor por defecto si no hay datos
    df_base = None
    if df_corte_json:
        df_base = pd.read_json(df_corte_json, orient='split')
    elif df_filtrado_json:
        df_base = pd.read_json(df_filtrado_json, orient='split')
    elif df_json:
        df_base = pd.read_json(df_json, orient='split')
    if df_base is not None and 'tiempo' in df_base.columns:
        t = df_base['tiempo'].values
        if len(t) > 1:
            dt = np.median(np.diff(t))
            fs = 1 / dt
            min_window = CONFIG.VENTANAS_WATERFALL['MINIMO']
            min_val = round(min_window / fs, 2)  # Mínimo real según puntos y fs, dos decimales
            duracion_total = t[-1] - t[0]
            max_val = max(min_val, round(float(duracion_total), 2))  # dos decimales
    return min_val, max_val

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                        # --- Callback para mostrar el rango permitido junto al input ---
                                        
@app.callback(Output('input-duracion-segmento', 'value'),
              Input('input-duracion-segmento', 'min'),
              Input('input-duracion-segmento', 'max'),
              State('input-duracion-segmento', 'value'),
             )

def sincronizar_valor_duracion_segmento(min_val, max_val, valor_actual):
    min_val = round(float(min_val), 2)
    max_val = round(float(max_val), 2)
    if valor_actual is None:
        return min_val
    valor_actual = round(float(valor_actual), 2)
    if valor_actual < min_val:
        return min_val
    elif valor_actual > max_val:
        return max_val
    else:
        return valor_actual

@app.callback(Output('texto-rango-duracion-segmento', 'children'),
              Input('input-duracion-segmento', 'min'),
              Input('input-duracion-segmento', 'max')
             )

def mostrar_rango_duracion_segmento(min_val, max_val):
    return f"Rango permitido: {min_val:.2f} s – {max_val:.2f} s"

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                        # --- Funciones de ventaneo para análisis transitorio ---

from dynamic_stiffness_analyzer.signal_processing.windowing import (
    estimate_adaptive_tau,
    ventana_exponencial,
    ventana_fuerza_adaptativa,
)

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                            # --- Callback para cargar el DataFrame filtrado desde el almacenamiento ---

@app.callback(Output('store-df-filtrado', 'data'),
              Output('mensaje-filtro', 'children'),
              Input('boton-aplicar-filtros', 'n_clicks'),
              State('store-df', 'data'),
              State('store-df-corte', 'data'),
              State('selector-multi', 'value'),
              State('selector-eje', 'value'),
              State('input-mediana', 'value'),
              State('input-highpass', 'value'),
              State('input-bandpass-multibanda', 'value'),
              State('toggle-mediana', 'value'),
              State('toggle-highpass', 'value'),
              State('toggle-bandpass', 'value'),
              prevent_initial_call=True
             )

def aplicar_filtros(n_clicks, df_json, df_corte_json, seleccion_multi, seleccion_eje, mediana_val, highpass_val,
                    bandpass_multibanda, toggle_mediana, toggle_highpass, toggle_bandpass):
    if n_clicks is None or n_clicks == 0:
        return no_update, no_update
    if df_json is None:
        return None, html.Div("No hay datos para filtrar", style={'color': 'red'})
    try:
        df = pd.read_json(df_json, orient='split')

        # Validaciones básicas
        if df.empty or 'tiempo' not in df.columns:
            return None, html.Div("Datos inválidos", style={'color': 'red'})

        # Calcular parámetros de tiempo
        t = df['tiempo'].values
        dt = np.median(np.diff(t))
        fs = 1 / dt

        # Aplicar filtros usando la función corregida
        df_filtrado, mensajes_filtro, _ = filtrar_senal(df, seleccion_multi, seleccion_eje, fs, mediana_val, highpass_val,
                                                        bandpass_multibanda, toggle_mediana, toggle_highpass, toggle_bandpass)

        # Preparar mensaje de éxito
        mensaje = html.Div([
            html.Span("✅ Filtros aplicados correctamente", style={'color': 'green', 'fontWeight': 'bold'}),
            html.Br(),
            html.Span(f"Señales procesadas: {len(seleccion_multi or [])}", style={'color': 'white'})])
        return df_filtrado.to_json(orient='split'), mensaje
    except Exception as e:
        print(f"[ERROR] Error aplicando filtros: {e}")
        return None, html.Div(f"Error: {str(e)[:50]}", style={'color': 'red'})

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                    # --- Función modular para filtrar la señal ---

from dynamic_stiffness_analyzer.signal_processing.filters import filtrar_senal

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                    # --- Callback para aplicar el corte de señal por tiempo ---

@app.callback(Output('store-df-corte', 'data'),
              Output('mensaje-corte', 'children'),
              Input('boton-aplicar-corte', 'n_clicks'),
              State('input-corte-inicio', 'value'),
              State('input-corte-fin', 'value'),
              State('store-df-filtrado', 'data'),
              State('store-df', 'data'),
              State('selector-multi', 'value'),
              prevent_initial_call=True
             )

def aplicar_corte(n_clicks, inicio, fin, df_filtrado_json, df_json, señales_seleccionadas):
    if n_clicks is None or (df_filtrado_json is None and df_json is None):
        return no_update, ''
    try:
        df = pd.read_json(df_filtrado_json or df_json, orient='split')
    except Exception:
        return no_update, 'Datos inválidos.'
    try:
        from dynamic_stiffness_analyzer.signal_processing.cutting import aplicar_corte_df
        df_corte, mensaje = aplicar_corte_df(df, inicio, fin, señales_seleccionadas)
        return df_corte.to_json(date_format='iso', orient='split'), mensaje
    except Exception as e:
        return no_update, str(e)

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                            # --- Callback para validar masa del martillo ---

from dynamic_stiffness_analyzer.services.validation import (
    validar_masa_martillo as _validar_masa_martillo,
)

def validar_masa_martillo(masa):
    # Delegado al módulo de servicios para evitar duplicar lógica
    return _validar_masa_martillo(masa)

@app.callback(Output('mensaje-masa-martillo', 'children'),
              Input('boton-aplicar-masa', 'n_clicks'),
              Input('input-masa-martillo', 'value'),
              State('input-masa-martillo', 'value'),
              prevent_initial_call=True
             )

def actualizar_mensaje_masa(n_clicks_boton, masa_input, masa_state):
    trigger_id = ctx.triggered_id if hasattr(ctx, 'triggered_id') else None
    if trigger_id == 'boton-aplicar-masa' and n_clicks_boton > 0:

        # Usuario hizo clic en "Aplicar masa"
        masa_validada, _ = validar_masa_martillo(masa_state)
        return f"✓ Masa aplicada: {masa_validada} kg - Los cálculos se actualizarán automáticamente"
    elif trigger_id == 'input-masa-martillo':

        # Usuario está cambiando el valor
        _, mensaje = validar_masa_martillo(masa_input)
        return f"⚠ {mensaje} - Haga clic en 'Aplicar masa' para confirmar"
    return ""

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                                # --- Callbacks de control de estado de botones ---

# Callback para controlar el estado del botón de masa del martillo
@app.callback(Output('boton-aplicar-masa', 'disabled'),
              Output('boton-aplicar-masa', 'style'),
              Output('icono-masa', 'children'),
              Output('icono-masa', 'style'),
              Input('store-df', 'data'),
              Input('input-masa-martillo', 'value'),
              Input('boton-aplicar-masa', 'n_clicks'),
              prevent_initial_call=True
             )

def controlar_estado_masa(df_json, masa_valor, n_clicks_masa):

    # Detectar si se acaba de hacer clic (estado procesando)
    ctx_triggered = ctx.triggered_id if hasattr(ctx, 'triggered_id') else None
    if df_json is None:

        # Sin datos cargados
        return True, {'backgroundColor': '#6c757d',
                      'color': 'white',
                      'fontWeight': 'bold',
                      'borderRadius': '4px',
                      'border': 'none',
                      'padding': '8px 15px',
                      'marginRight': '15px'}, '⚠', {'marginRight': '5px',
                                                    'fontSize': '16px',
                                                    'color': '#ffc107'}

    # ESTADO PROCESANDO: Si se acaba de hacer clic en el botón
    if ctx_triggered == 'boton-aplicar-masa' and n_clicks_masa > 0:
        return True, {'backgroundColor': '#ffc107',
                      'color': 'white',
                      'fontWeight': 'bold',
                      'borderRadius': '4px',
                      'border': 'none',
                      'padding': '8px 15px',
                      'marginRight': '15px'}, '⏳', {'marginRight': '5px',
                                                    'fontSize': '16px',
                                                    'color': 'white'}
    masa_validada, _ = validar_masa_martillo(masa_valor)
    if n_clicks_masa > 0 and masa_validada == masa_valor:

        # Masa aplicada correctamente - VERDE COMPLETADO
        return True, {'backgroundColor': '#28a745',
                      'color': 'white',
                      'fontWeight': 'bold',
                      'borderRadius': '4px',
                      'border': 'none',
                      'padding': '8px 15px',
                      'marginRight': '15px'}, '✓', {'marginRight': '5px',
                                                    'fontSize': '16px',
                                                    'color': 'white'}
    else:

        # Listo para aplicar - AZUL DISPONIBLE
        return False, {'backgroundColor': '#17a2b8',
                       'color': 'white',
                       'fontWeight': 'bold',
                       'borderRadius': '4px',
                       'border': 'none',
                       'padding': '8px 15px',
                       'marginRight': '15px'}, '◯', {'marginRight': '5px',
                                                     'fontSize': '16px',
                                                     'color': 'white'}

# Callback para controlar el estado visual del botón de filtros (solo estilo e iconos)
@app.callback(Output('boton-aplicar-filtros', 'style'),
              Output('icono-filtros', 'children'),
              Output('icono-filtros', 'style'),
              Input('store-df', 'data'),
              Input('store-df-corte', 'data'),
              Input('toggle-mediana', 'value'),
              Input('toggle-highpass', 'value'),
              Input('toggle-bandpass', 'value'),
              Input('boton-aplicar-filtros', 'n_clicks'),
              prevent_initial_call=True
             )

def controlar_estilo_filtros(df_json, df_corte_json, toggle_med, toggle_hp, toggle_bp, n_clicks_filtros):

    # Detectar si se acaba de hacer clic (estado procesando)
    ctx_triggered = ctx.triggered_id if hasattr(ctx, 'triggered_id') else None
    if df_json is None:

        # Sin datos - Gris con advertencia
        return {'backgroundColor': '#6c757d',
                'color': 'white',
                'fontWeight': 'bold',
                'borderRadius': '4px',
                'border': 'none',
                'padding': '8px 15px',
                'marginRight': '15px'}, '⚠', {'marginRight': '5px',
                                              'fontSize': '16px',
                                              'color': '#ffc107'}
    if df_corte_json is not None:

        # Ya hay corte aplicado - ROJO BLOQUEADO
        return {'backgroundColor': '#dc3545',
                'color': 'white',
                'fontWeight': 'bold',
                'borderRadius': '4px',
                'border': 'none',
                'padding': '8px 15px',
                'marginRight': '15px'}, '✗', {'marginRight': '5px',
                                              'fontSize': '16px',
                                              'color': 'white'}

    # ESTADO PROCESANDO: Si se acaba de hacer clic en el botón
    if ctx_triggered == 'boton-aplicar-filtros' and n_clicks_filtros > 0:
        return {'backgroundColor': '#ffc107',
                'color': 'white',
                'fontWeight': 'bold',
                'borderRadius': '4px',
                'border': 'none',
                'padding': '8px 15px',
                'marginRight': '15px'}, '⏳', {'marginRight': '5px',
                                              'fontSize': '16px',
                                              'color': 'white'}

    # Verificar si hay algún filtro activo
    algun_filtro_activo = (toggle_med == 'yes') or (toggle_hp == 'yes') or (toggle_bp == 'yes')
    if not algun_filtro_activo:

        # Sin filtros activos - Gris
        return {'backgroundColor': '#6c757d',
                'color': 'white',
                'fontWeight': 'bold',
                'borderRadius': '4px',
                'border': 'none',
                'padding': '8px 15px',
                'marginRight': '15px'}, '○', {'marginRight': '5px',
                                              'fontSize': '16px',
                                              'color': '#ffc107'}
    if n_clicks_filtros > 0:

        # Filtros aplicados - Verde completado
        return {'backgroundColor': '#28a745',
                'color': 'white',
                'fontWeight': 'bold',
                'borderRadius': '4px',
                'border': 'none',
                'padding': '8px 15px',
                'marginRight': '15px'}, '✓', {'marginRight': '5px',
                                              'fontSize': '16px',
                                              'color': 'white'}
    else:

        # Listo para aplicar filtros - Azul disponible
        return {'backgroundColor': '#17a2b8',
                'color': 'white',
                'fontWeight': 'bold',
                'borderRadius': '4px',
                'border': 'none',
                'padding': '8px 15px',
                'marginRight': '15px'}, '◯', {'marginRight': '5px',
                                              'fontSize': '16px',
                                              'color': 'white'}

# Callback original para deshabilitar el botón de filtros si ya hay corte (funcionalidad core)
@app.callback(Output('boton-aplicar-filtros', 'disabled'),
              Input('store-df-corte', 'data'),
              Input('store-df', 'data'),
              Input('toggle-mediana', 'value'),
              Input('toggle-highpass', 'value'),
              Input('toggle-bandpass', 'value'),
              Input('boton-aplicar-filtros', 'n_clicks'),
              prevent_initial_call=True
             )

def deshabilitar_filtro_si_corte(df_corte_json, df_json, toggle_med, toggle_hp, toggle_bp, n_clicks_filtros):

    # Detectar si se acaba de hacer clic (estado procesando)
    ctx_triggered = ctx.triggered_id if hasattr(ctx, 'triggered_id') else None

    # ESTADO PROCESANDO: Si se acaba de hacer clic, bloquear inmediatamente
    if ctx_triggered == 'boton-aplicar-filtros' and n_clicks_filtros > 0:
        return True  # Bloqueado durante procesamiento

    # Bloqueo por corte activado (funcionalidad original)
    if df_corte_json is not None:
        return True  # Bloqueado porque ya hay corte

    # Bloqueo por falta de datos
    if df_json is None:
        return True  # No hay datos cargados

    # Bloqueo por falta de filtros activos
    algun_filtro_activo = (toggle_med == 'yes') or (toggle_hp == 'yes') or (toggle_bp == 'yes')
    if not algun_filtro_activo:
        return True  # No hay filtros activos

    # Bloqueo si ya se aplicaron filtros 
    if n_clicks_filtros > 0:
        return True  # Ya se aplicaron los filtros

    # DISPONIBLE: Datos cargados + filtros activos + no hay corte + no aplicado aún
    return False

# Callback para controlar el estado del botón de corte
@app.callback(Output('boton-aplicar-corte', 'disabled'),
              Output('boton-aplicar-corte', 'style'),
              Output('icono-corte', 'children'),
              Output('icono-corte', 'style'),
              Input('store-df', 'data'),
              Input('store-df-filtrado', 'data'),
              Input('input-corte-inicio', 'value'),
              Input('input-corte-fin', 'value'),
              Input('boton-aplicar-corte', 'n_clicks'),
              prevent_initial_call=True
             )

def controlar_estado_corte(df_json, df_filtrado_json, inicio, fin, n_clicks_corte):

    # Detectar si se acaba de hacer clic (estado procesando)
    ctx_triggered = ctx.triggered_id if hasattr(ctx, 'triggered_id') else None
    if df_json is None:

        # Sin datos
        return True, {'marginLeft': '30px',
                      'backgroundColor': '#6c757d',
                      'color': 'white',
                      'fontWeight': 'bold',
                      'borderRadius': '4px',
                      'border': 'none',
                      'padding': '8px 15px'}, '⚠', {'marginRight': '5px',
                                                    'fontSize': '16px',
                                                    'color': '#ffc107'}

    # ESTADO PROCESANDO: Si se acaba de hacer clic en el botón
    if ctx_triggered == 'boton-aplicar-corte' and n_clicks_corte > 0:
        return True, {'marginLeft': '30px',
                      'backgroundColor': '#ffc107',
                      'color': 'white',
                      'fontWeight': 'bold',
                      'borderRadius': '4px',
                      'border': 'none',
                      'padding': '8px 15px'}, '⏳', {'marginRight': '5px',
                                                    'fontSize': '16px',
                                                    'color': 'white'}

    # Validar rango de corte
    if inicio is None or fin is None or inicio >= fin:

        # Rango inválido
        return True, {'marginLeft': '30px',
                      'backgroundColor': '#6c757d',
                      'color': 'white',
                      'fontWeight': 'bold',
                      'borderRadius': '4px',
                      'border': 'none',
                      'padding': '8px 15px'}, '○', {'marginRight': '5px',
                                                    'fontSize': '16px',
                                                    'color': '#ffc107'}
    if n_clicks_corte > 0:

        # Corte aplicado - Verde completado
        return True, {'marginLeft': '30px',
                      'backgroundColor': '#28a745',
                      'color': 'white',
                      'fontWeight': 'bold',
                      'borderRadius': '4px',
                      'border': 'none',
                      'padding': '8px 15px'}, '✓', {'marginRight': '5px',
                                                    'fontSize': '16px',
                                                    'color': 'white'}
    else:

        # Listo para aplicar corte - Azul disponible
        return False, {'marginLeft': '30px',
                       'backgroundColor': '#17a2b8',
                       'color': 'white',
                       'fontWeight': 'bold',
                       'borderRadius': '4px',
                       'border': 'none',
                       'padding': '8px 15px'}, '◯', {'marginRight': '5px',
                                                     'fontSize': '16px',
                                                     'color': 'white'}

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                                    # --- Callback principal ---

@app.callback(Output('grafico-tiempo', 'figure'),
              Output('grafico-fft', 'figure'),
              Output('grafico-waterfall', 'figure'),
              Output('amortiguamiento-tables', 'children'),
              Output('grafico-desplazamiento', 'figure'),
              Output('grafico-coherencia', 'figure'),
              Output('selector-curvas', 'value'),
              Output('selector-curvas', 'options'),
              Output('estado-fijar-vista', 'data'),
              Output('boton-fijar-vista', 'style'),
              Output('input-mediana', 'value'),
              Output('input-highpass', 'value'),
              Output('input-bandpass-multibanda', 'value'),
              Input('selector-multi', 'value'),
              Input('selector-eje', 'value'),
              Input('escala-x', 'value'),
              Input('escala-y', 'value'),
              Input('selector-curvas', 'value'),
              Input('boton-reset', 'n_clicks'),
              Input('boton-fijar-vista', 'n_clicks'),
              Input('store-df', 'data'),
              Input('boton-aplicar-filtros', 'n_clicks'),
              Input('store-df-corte', 'data'),
              Input('store-df-filtrado', 'data'),
              Input('boton-aplicar-duracion-segmento', 'n_clicks'),
              Input('boton-aplicar-masa', 'n_clicks'),
              State('input-masa-martillo', 'value'),
              State('input-mediana', 'value'),
              State('input-highpass', 'value'),
              State('input-bandpass-multibanda', 'value'),
              State('selector-curvas', 'value'),
              State('estado-fijar-vista', 'data'),
              State('toggle-mediana', 'value'),
              State('toggle-highpass', 'value'),
              State('toggle-bandpass', 'value'),
              State('store-df-filtrado', 'data'),
              State('mensaje-filtro', 'children'),
              State('input-duracion-segmento', 'value'),
             )

def actualizar_graficos(seleccion_multi, seleccion_eje, escala_x, escala_y, curvas_enfasis_input, n_clicks_reset, n_clicks_fijar,
                        df_json, n_clicks_aplicar, df_corte_json, df_filtrado_json, n_clicks_aplicar_duracion,
                        n_clicks_aplicar_masa, masa_martillo, mediana_val, highpass_val, bandpass_multibanda, curvas_enfasis_state,
                        estado_fijar_vista, toggle_mediana, toggle_highpass, toggle_bandpass, store_df_filtrado, mensaje_filtro,
                        duracion_segmento):
    try:
        
        # Detectar cambios que requieren limpieza de caché
        trigger_id = ctx.triggered_id if hasattr(ctx, 'triggered_id') else None

        # Limpiar caché cuando cambian datos base o se aplican filtros/cortes
        triggers_limpiar_cache = ['store-df',  # Nuevo archivo cargado
                                  'boton-aplicar-filtros',  # Filtros aplicados
                                  'boton-aplicar-corte',  # Corte aplicado
                                  'boton-aplicar-masa'  # Masa del martillo cambiada
                                 ]
        if USAR_CACHE and trigger_id in triggers_limpiar_cache:
            cache_computacional.limpiar_cache()
            print(f"[CACHÉ] Caché limpiado por cambio en: {trigger_id}")
        df_original = pd.read_json(df_json, orient='split') if df_json else None

        # Debug del estado inicial
        print(f"[DEBUG] Estado inicial - df_json existe: {df_json is not None}")
        if df_json:
            print(f"[DEBUG] Tamaño df_json: {len(df_json)} caracteres")
        if df_original is not None:
            print(f"[DEBUG] df_original cargado: shape={df_original.shape}, columnas={list(df_original.columns)}")

        # Si no hay datos cargados, devolver figuras vacías
        if df_json is None or df_original is None:
            print("[ERROR] Sin datos cargados")
            return generar_graficos_vacios()

        # Verificar que hay columnas de tiempo y respuesta en el DataFrame
        if df_original.empty or 'tiempo' not in df_original.columns:
            print(f"[ERROR] DataFrame inválido - empty: {df_original.empty}, tiene tiempo: {'tiempo' in df_original.columns}")
            return generar_graficos_vacios()

        # Obtener el trigger_id de la acción que disparó el callback
        trigger_id = ctx.triggered_id if hasattr(ctx, 'triggered_id') else (
            ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None)

        # Inicializa siempre las variables de store para evitar errores de referencia
        df_filtrado_json = df_filtrado_json if 'df_filtrado_json' in locals() or 'df_filtrado_json' in globals() else None

        # Selección del DataFrame base para graficar
        df_base = None
        if df_corte_json is not None and df_corte_json != '':
            try:
                df_base = pd.read_json(df_corte_json, orient='split')
                if df_base.empty or 'tiempo' not in df_base.columns:
                    df_base = None
            except Exception:
                df_base = None
        elif df_filtrado_json is not None and df_filtrado_json != '':
            try:
                df_base = pd.read_json(df_filtrado_json, orient='split')
                if df_base.empty or 'tiempo' not in df_base.columns:
                    df_base = None
            except Exception:
                df_base = None
        elif df_json is not None and df_json != '':
            try:
                df_base = pd.read_json(df_json, orient='split')
                if df_base.empty or 'tiempo' not in df_base.columns:
                    df_base = None
            except Exception:
                df_base = None
        if df_base is None:
            return generar_graficos_vacios()
        df = df_base.copy()

        # Validar que el DataFrame resultante no esté vacío y tenga datos válidos
        if df.empty or len(df) < 2:
            return generar_graficos_vacios()

        # Eliminar filas con NaN o infinitos en columnas críticas
        columnas_criticas = ['tiempo'] + [col for col in df.columns if col.startswith(('accel_', 'fuerza'))]
        df_clean = df[columnas_criticas].replace([np.inf, -np.inf], np.nan).dropna()
        if df_clean.empty or len(df_clean) < 2:
            return generar_graficos_vacios()

        # Actualizar df con datos limpios pero mantener todas las columnas originales
        df.loc[df_clean.index, columnas_criticas] = df_clean[columnas_criticas]
        df = df.loc[df_clean.index].copy()
    except Exception as e:
        print(f"Error crítico al inicio de actualizar_graficos: {e}")
        return generar_graficos_vacios()

    # Inicialización de variables de estado
    filtro_aplicado = False
    mensajes_filtro = []
    df_filtrado = None

    # Si los selectores están vacíos (primera carga tras subir archivo), fuerza valores por defecto
    if not seleccion_multi:
        seleccion_multi = ['accel_x']
    if not seleccion_eje:
        seleccion_eje = 'accel_x'

    # --- Parsear frecuencias_centrales una sola vez ---
    frecuencias_centrales = []
    if bandpass_multibanda:
        try:
            frecuencias_centrales = [float(f.strip()) for f in bandpass_multibanda.split(',') if f.strip()]
        except Exception:
            frecuencias_centrales = []

    # Hacer frecuencias_centrales disponible para filtrar_senal
    filtrar_senal.frecuencias_centrales = frecuencias_centrales

    # Determinar el DataFrame a graficar con validaciones adicionales
    try:
        if df_corte_json:
            df = pd.read_json(df_corte_json, orient='split')
            print("[DEBUG] Graficando con df_corte_json (corte aplicado)")
            filtro_aplicado = False
            mensajes_filtro = []
        elif df_filtrado_json:
            df = pd.read_json(df_filtrado_json, orient='split')
            print("[DEBUG] Graficando con df_filtrado_json (filtro aplicado)")
            filtro_aplicado = True
            mensajes_filtro = []
        else:
            df = df_base.copy()
            print("[DEBUG] Graficando con df_base (sin filtro ni corte)")
            filtro_aplicado = False
            mensajes_filtro = []

        # Validar nuevamente que el DataFrame final tiene datos válidos
        if df.empty or len(df) < 2 or 'tiempo' not in df.columns:
            print("[ERROR] DataFrame final inválido o vacío")
            return generar_graficos_vacios()
        print(f"[DEBUG] DataFrame para graficar: columnas={list(df.columns)}, shape={df.shape}")

        # Validar selecciones con valores por defecto seguros
        columnas_disponibles = [col for col in df.columns if col != 'tiempo']
        print(f"[DEBUG] Columnas disponibles en DataFrame: {columnas_disponibles}")
        if not columnas_disponibles:
            print("[ERROR] No hay columnas de datos disponibles")
            return generar_graficos_vacios()

        # Si los selectores están vacíos o contienen columnas inexistentes, usar valores por defecto
        if not seleccion_multi or not any(col in df.columns for col in seleccion_multi):
            if 'accel_x' in df.columns:
                seleccion_multi = ['accel_x']
            else:
                seleccion_multi = [columnas_disponibles[0]]  # Usar la primera columna disponible
            print(f"[DEBUG] Seleccion_multi ajustada a: {seleccion_multi}")
        if not seleccion_eje or seleccion_eje not in df.columns:
            if 'accel_x' in df.columns:
                seleccion_eje = 'accel_x'
            else:
                seleccion_eje = columnas_disponibles[0]  # Usar la primera columna disponible
            print(f"[DEBUG] Seleccion_eje ajustada a: {seleccion_eje}")

        # Filtrar seleccion_multi para incluir solo columnas existentes
        seleccion_multi = [col for col in seleccion_multi if col in df.columns]
        if not seleccion_multi:
            seleccion_multi = [columnas_disponibles[0]]
        print(f"[DEBUG] Selectores finales - multi: {seleccion_multi}, eje: {seleccion_eje}")

        # Debug de columnas seleccionadas
        for col in seleccion_multi:
            if col in df.columns:
                y = df[col].values
                if len(y) > 0 and np.isfinite(y).any():
                    y_finite = y[np.isfinite(y)]
                    if len(y_finite) > 0:
                        print(f"[DEBUG] Graficando columna '{col}': min={np.min(y_finite):.4f}, max={np.max(y_finite):.4f}, mean={np.mean(y_finite):.4f}, std={np.std(y_finite):.4f}")
                    else:
                        print(f"[WARNING] Columna '{col}' no tiene valores finitos")
                else:
                    print(f"[WARNING] Columna '{col}' está vacía o solo contiene valores no finitos")

        # --- Método de diagnóstico y regeneración de dt ---
        t = df['tiempo'].values
        if len(t) < 2:
            print("[ERROR] Insuficientes puntos de tiempo")
            return generar_graficos_vacios()

        # 1. Diagnóstico de regularidad temporal
        dt_values = np.diff(t)

        # Filtrar valores no válidos antes del cálculo
        dt_values_valid = dt_values[dt_values > 0]
        if len(dt_values_valid) == 0:
            print("[ERROR] No hay intervalos de tiempo válidos")
            return generar_graficos_vacios()
        dt_original = np.median(dt_values_valid)
        if dt_original <= 0:
            print("[WARNING] Intervalo de tiempo inválido calculado")

            # Fallback: calcular dt desde el rango total
            dt_original = (t[-1] - t[0]) / (len(t) - 1)
            if dt_original <= 0:
                print("[ERROR] No se puede calcular dt válido - usando valor por defecto")
                dt_original = 0.001  # 1ms por defecto
                fs = 1000.0
                print(f"[INFO] Usando dt={dt_original:.6f}, fs={fs:.2f} Hz por defecto")
            else:
                fs = 1 / dt_original
                print(f"[INFO] dt calculado desde rango total: {dt_original:.6f}, fs={fs:.2f} Hz")
        else:
            fs = 1 / dt_original
            print(f"[INFO] dt válido desde mediana: {dt_original:.6f}, fs={fs:.2f} Hz")

        # Continuar con el diagnóstico solo si tenemos un dt válido
        dt_std = np.std(dt_values_valid)
        dt_mean = np.mean(dt_values_valid)
        irregularidad_relativa = dt_std / dt_mean if dt_mean > 0 else 1.0
        print(f"[DEBUG] Diagnóstico temporal original:")
        print(f"  - dt_mean: {dt_mean:.6f} s")
        print(f"  - dt_std: {dt_std:.6f} s")
        print(f"  - Irregularidad relativa: {irregularidad_relativa:.4f} ({irregularidad_relativa * 100:.2f}%)")
        print(f"  - Valores dt válidos: {len(dt_values_valid)}/{len(dt_values)}")

        # 2. Criterio objetivo: si la irregularidad supera el 5%, regenerar
        umbral_irregularidad = CONFIG.TOLERANCIAS['IRREGULARIDAD_TEMPORAL']  # 5%
        tiempo_regenerado = False
        if irregularidad_relativa > umbral_irregularidad:
            print(f"[WARNING] Irregularidad temporal detectada ({irregularidad_relativa * 100:.2f}% > {umbral_irregularidad * 100:.1f}%)")
            print("[INFO] Regenerando vector de tiempo uniforme...")

            # Regenerar vector de tiempo uniforme
            t_inicial = t[0]
            t_final = t[-1]
            n_puntos = len(t)

            # Verificar que el rango de tiempo es válido
            if t_final <= t_inicial:
                print("[WARNING] Rango de tiempo inválido - usando tiempo por defecto")
                t_nuevo = np.linspace(0, n_puntos * dt_original, n_puntos)
            else:
                t_nuevo = np.linspace(t_inicial, t_final, n_puntos)

            # Reemplazar en el DataFrame
            df['tiempo'] = t_nuevo
            t = t_nuevo

            # Recalcular parámetros
            dt_nuevo = (t_nuevo[-1] - t_nuevo[0]) / (n_puntos - 1) if n_puntos > 1 else dt_original
            dt_values_nuevo = np.diff(t_nuevo)
            dt_std_nuevo = np.std(dt_values_nuevo)
            irregularidad_nueva = dt_std_nuevo / dt_nuevo if dt_nuevo > 0 else 0.0
            print(f"[INFO] Tiempo regenerado exitosamente:")
            print(f"  - dt_nuevo: {dt_nuevo:.6f} s")
            print(f"  - Irregularidad nueva: {irregularidad_nueva:.6f} ({irregularidad_nueva * 100:.4f}%)")
            dt = dt_nuevo
            fs = 1 / dt
            tiempo_regenerado = True
        else:
            print(f"[INFO] Vector de tiempo regular ({irregularidad_relativa * 100:.2f}% ≤ {umbral_irregularidad * 100:.1f}%)")
            dt = dt_original

        # Verificación final de dt
        if dt <= 0 or not np.isfinite(dt):
            print("[ERROR] dt final inválido - forzando valor por defecto")
            dt = 0.001  # 1ms
            fs = 1000.0
            tiempo_regenerado = True
        else:
            fs = 1 / dt
        print(f"[DEBUG] Parámetros temporales finales: dt={dt:.6f}, fs={fs:.2f} Hz, regenerado={tiempo_regenerado}")

        # Lógica del botón fijar vista 3D con validación
        try:
            curvas_enfasis = [] if trigger_id == 'boton-reset' else (curvas_enfasis_input or [])
            if trigger_id == 'boton-fijar-vista':
                estado_fijar_vista = not estado_fijar_vista
            if estado_fijar_vista:
                estilo_fijar = {'backgroundColor': "#f01717",
                                'color': 'white', 'fontWeight': 'bold',
                                'borderRadius': '4px',
                                'border': 'none',
                                'padding': '8px 15px'}
            else:
                estilo_fijar = {'backgroundColor': "#7C8085",
                                'color': 'white',
                                'fontWeight': 'bold',
                                'borderRadius': '4px',
                                'border': 'none',
                                'padding': '8px 15px'}
        except Exception as e:
            print(f"[WARNING] Error en lógica de vista: {e}")
            curvas_enfasis = []
            estado_fijar_vista = False
            estilo_fijar = {'backgroundColor': "#7C8085",
                            'color': 'white',
                            'fontWeight': 'bold',
                            'borderRadius': '4px',
                            'border': 'none',
                            'padding': '8px 15px'}
    except Exception as e:
        print(f"[ERROR] Error en preparación de datos: {e}")
        return generar_graficos_vacios()

######################################################################################################################################
                                        # --- Gráfico de tiempo con manejo de errores ---

    try:

        # Usar siempre la función optimizada (maneja automáticamente datasets grandes y pequeños)
        from dynamic_stiffness_analyzer.visualization.time_plot import generar_grafico_tiempo_optimizado
        fig_tiempo = generar_grafico_tiempo_optimizado(df, seleccion_multi, df_original, filtro_aplicado, df_corte_json)
    except Exception as e:
        print(f"[ERROR] Error generando gráfico de tiempo: {e}")
        fig_tiempo = generar_figura_vacia("Error en gráfico de tiempo")

######################################################################################################################################
                                            # --- Gráfico FFT con manejo de errores ---

    try:

        # Usar siempre la función adaptativa (maneja automáticamente caché y optimización)
        from dynamic_stiffness_analyzer.visualization.fft_plot import generar_grafico_fft_optimizado
        fig_fft = generar_grafico_fft_optimizado(df, seleccion_multi, escala_x, escala_y)
    except Exception as e:
        print(f"[ERROR] Error generando gráfico FFT: {e}")
        fig_fft = generar_figura_vacia("Error en gráfico FFT")

######################################################################################################################################
                                        # --- Gráfico 3D waterfall con manejo de errores ---

    try:
        if df_corte_json is not None and df_corte_json != '':
            df_waterfall_json = df_corte_json
        elif df_filtrado_json is not None and df_filtrado_json != '':
            df_waterfall_json = df_filtrado_json
        else:
            df_waterfall_json = df_json

        # FORZAR limpieza del caché para aplicar correcciones de frecuencias
        if USAR_CACHE:
            cache_computacional.limpiar_cache()
            print("[DEBUG] Caché limpiado forzadamente para aplicar correcciones de waterfall")

        # Función que detecta automáticamente si necesita optimización
        from dynamic_stiffness_analyzer.visualization.waterfall_plot import generar_waterfall_adaptativo
        fig_waterfall, datos_waterfall = generar_waterfall_adaptativo(df_waterfall_json, seleccion_eje, escala_x, escala_y, curvas_enfasis, estado_fijar_vista, duracion_segmento)

        # Opciones de curvas para el selector
        opciones_curvas = []
        if datos_waterfall and isinstance(datos_waterfall, list):
            try:

                # Agrupar por segmento para evitar duplicados
                segmentos_unicos = {}
                for d in datos_waterfall:
                    if isinstance(d, dict) and 'segmento' in d and 'tiempo_central' in d:
                        seg = d['segmento']
                        if seg not in segmentos_unicos:
                            segmentos_unicos[seg] = d['tiempo_central']
                opciones_curvas += [{'label': f'Curva {seg} - {tiempo:.2f}s', 'value': str(seg - 1)}
                                    for seg, tiempo in sorted(segmentos_unicos.items())]
            except Exception as e:
                print(f"[WARNING] Error generando opciones de curvas: {e}")
                opciones_curvas = []
        actualizar_graficos.datos_waterfall = datos_waterfall
    except Exception as e:
        print(f"[ERROR] Error generando waterfall: {e}")
        fig_waterfall = generar_figura_vacia("Error en gráfico Waterfall")
        opciones_curvas = []
        datos_waterfall = []

    # Mapas de color y etiquetas para los ejes
    color_map = {'accel_x': 'red', 'accel_y': 'green', 'accel_z': 'blue'}
    label_map = {'accel_x': 'X', 'accel_y': 'Y', 'accel_z': 'Z'}

######################################################################################################################################
                                # --- Cálculo de rigidez dinámica y variables asociadas ---

    try:

        # Inicializar variables para caso de error
        fK = np.array([])
        S_ff = np.array([])
        magK = np.array([])
        phaseK = np.array([])
        fig_damping = html.Div("Sin datos para calcular amortiguamiento")

        # Verificar que el eje seleccionado es válido y existe en el DataFrame
        if seleccion_eje in ['accel_x', 'accel_y',
                             'accel_z'] and seleccion_eje in df.columns and 'fuerza' in df.columns:

            # Verificar que hay suficientes datos para FRF
            if len(df) < 1024:  # Mínimo para análisis espectral
                print(f"[WARNING] Insuficientes datos para FRF: {len(df)} puntos")
                raise ValueError("Insuficientes datos para análisis FRF")

            # Validar y usar masa del martillo desde input del usuario
            MASA_MARTILLO_KG, _ = validar_masa_martillo(masa_martillo)

            # Obtener señales con validación
            fuerza_g = df['fuerza'].values
            accel_g = df[seleccion_eje].values

            # Verificar que las señales no están vacías y tienen valores finitos
            if len(fuerza_g) == 0 or len(accel_g) == 0:
                raise ValueError("Señales vacías")
            if not np.isfinite(fuerza_g).any() or not np.isfinite(accel_g).any():
                raise ValueError("Señales contienen solo valores no finitos")

            # Ventaneo de fuerza y aceleración antes de análisis de FRF
            fuerza_g = ventana_fuerza_adaptativa(fuerza_g, fs)
            fuerza_N = fuerza_g * MASA_MARTILLO_KG * 9.81
            accel_g = ventana_exponencial(accel_g, fs)
            accel = accel_g * 9.81

            # Verificar que las señales ventaneadas siguen siendo válidas
            if not np.isfinite(fuerza_N).any() or not np.isfinite(accel).any():
                raise ValueError("Señales inválidas después de ventaneo")

            # Parámetros adaptativos para Welch según longitud de datos
            nperseg = min(1024, len(df) // 6)  # Al menos 6 segmentos
            nperseg = max(256, nperseg)  # Mínimo 256 puntos por segmento
            noverlap = nperseg // 2
            print(f"[DEBUG] Parámetros Welch: nperseg={nperseg}, noverlap={noverlap}")

            # Cálculo de espectros
            fK, S_ff = welch(fuerza_N, fs=fs, window='hann', nperseg=nperseg, noverlap=noverlap)
            _, S_xf = csd(accel, fuerza_N, fs=fs, window='hann', nperseg=nperseg, noverlap=noverlap)
            _, S_xx = welch(accel, fs=fs, window='hann', nperseg=nperseg, noverlap=noverlap)

            # Verificar que los espectros son válidos
            if len(fK) == 0 or not np.isfinite(S_ff).any() or not np.isfinite(S_xf).any() or not np.isfinite(
                    S_xx).any():
                raise ValueError("Espectros inválidos")

            # Estimadores robustos de FRF usando los espectros calculados
            from dynamic_stiffness_analyzer.analysis.frf import (
                calculate_H1,
                calculate_H2,
                calculate_coherence,
                calculate_Hv,
            )

            from dynamic_stiffness_analyzer.analysis.dynamic_stiffness import detect_antiresonances, calculate_dynamic_stiffness_robust
            print(f"[DEBUG] Espectros calculados: fK shape={fK.shape}, S_ff shape={S_ff.shape}")

            # Selección del estimador usando las funciones
            H_frf = calculate_Hv(S_ff, S_xx, S_xf)
        else:
            print(f"[INFO] Eje {seleccion_eje} no válido o columnas faltantes para FRF")
    except Exception as e:
        print(f"[ERROR] Error en cálculo de FRF: {e}")

        # Mantener variables inicializadas para evitar errores posteriores
        fK = np.array([])
        S_ff = np.array([])
        magK = np.array([])
        phaseK = np.array([])
        fig_damping = html.Div(f"Error calculando amortiguamiento: {str(e)[:100]}")

    # Continuar con el cálculo de rigidez dinámica si hay datos válidos
    if len(fK) > 0 and len(S_ff) > 0:
        try:

            # Selección del estimador usando las funciones
            H_frf = calculate_Hv(S_ff, S_xx, S_xf)

            # Rigidez dinámica
            K_disp = calculate_dynamic_stiffness_robust(H_frf, fK, fK, S_ff, S_xx, S_xf)
            magK = np.abs(K_disp)
            phaseK = np.angle(K_disp, deg=True)

######################################################################################################################################
                                    # --- Visualización de tablas de amortiguamiento ---

            try:
                from dynamic_stiffness_analyzer.analysis.damping import calculo_amortiguamiento
                resultado_amort = calculo_amortiguamiento(df[seleccion_eje].values, fs, frecuencias_centrales)
                modos = resultado_amort.get('modos', [])
                zeta_global = resultado_amort.get('zeta_global', None)
                mensajes = resultado_amort.get('mensajes', [])
            except Exception as e:
                print(f"[WARNING] Error en cálculo de amortiguamiento: {e}")
                modos = []
                zeta_global = None
                mensajes = [f"Error en cálculo: {str(e)[:50]}"]

            def fmt(val, dec=4):
                if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
                    return '---'
                return f"{val:.{dec}f}"

            # Tabla de modos (frecuencia y zeta modal)
            data_modos = []
            for modo in modos:
                data_modos.append({
                    "Frecuencia (Hz)": fmt(modo.get('frecuencia')),
                    "ζ modal": fmt(modo.get('zeta'))})
            if not data_modos:
                data_modos = [{"Frecuencia (Hz)": '---', "ζ modal": '---'}]
            tabla_modos = dash_table.DataTable(columns=[{"name": "Frecuencia (Hz)", "id": "Frecuencia (Hz)"},
                                                        {"name": "ζ modal", "id": "ζ modal"}],
                                               data=data_modos, style_header={"backgroundColor": "#222",
                                                                              "color": "white",
                                                                              "fontWeight": "bold",
                                                                              "fontSize": 16},
                                               style_cell={"backgroundColor": "#333",
                                                           "color": "white",
                                                           "textAlign": "center",
                                                           "fontSize": 15},
                                               style_table={"width": "100%",
                                                            "marginBottom": "20px"},
                                              )

            # Tabla resumen global (ζ global y amortiguamiento físico por unidad de masa C/m)
            # Cálculo de C/m = 2*zeta*2*pi*f (N·s/mm), usando la frecuencia del primer modo detectado
            if zeta_global is not None and len(modos) > 0 and modos[0].get('frecuencia') is not None:
                freq_1 = modos[0]['frecuencia']
                zeta_g = zeta_global
                c_m = 2 * zeta_g * 2 * np.pi * freq_1  # N·s/m
                c_m_str = f"{c_m:.6f}"
            else:
                c_m_str = '---'
            data_global = [
                {"ζ global": fmt(zeta_global), "Amortiguamiento físico (por unidad de masa, C/m) [N·s/m]": c_m_str}]
            tabla_global = dash_table.DataTable(columns=[{"name": "ζ global", "id": "ζ global"},
                                                         {"name": "Amortiguamiento físico (por unidad de masa, C/m) [N·s/m]",
                                                          "id": "Amortiguamiento físico (por unidad de masa, C/m) [N·s/m]"}],
                                                data=data_global, style_header={"backgroundColor": "#222",
                                                                                "color": "white",
                                                                                "fontWeight": "bold",
                                                                                "fontSize": 16},
                                                style_cell={"backgroundColor": "#333",
                                                            "color": "white",
                                                            "textAlign": "center",
                                                            "fontSize": 15},
                                                style_table={"width": "100%",
                                                             "marginBottom": "20px"},
                                               )

            # Mostrar ambas tablas una debajo de la otra
            tablas_amort = html.Div([
                html.H4("Resumen global", style={"color": "white",
                                                 "marginBottom": "5px",
                                                 "marginTop": "0"}),
                tabla_global,
                html.H4("Resumen Modal", style={"color": "white",
                                                "marginBottom": "5px",
                                                "marginTop": "20px"}),
                tabla_modos,
                html.Div([
                    html.Div(msg, style={"color": "orange",
                                         "fontWeight": "bold",
                                         "marginTop": "10px"}) for msg in mensajes
                         ]) if mensajes else None
                                    ])
            fig_damping = tablas_amort
        except Exception as e:
            print(f"[ERROR] Error en cálculo avanzado de rigidez: {e}")

            # Valores por defecto en caso de error
            magK = np.array([])
            phaseK = np.array([])
            fig_damping = html.Div([
                html.H4("Error en cálculo de amortiguamiento", style={"color": "red",
                                                                      "marginBottom": "5px"}),
                html.Div(f"Error: {str(e)[:100]}", style={"color": "white",
                                                          "textAlign": "center"})])
    else:

        # Sin datos válidos para FRF - valores por defecto seguros
        fK = np.array([])
        S_ff = np.array([])
        magK = np.array([])
        phaseK = np.array([])
        fig_damping = html.Div("Sin datos suficientes para análisis de rigidez dinámica", style={"color": "orange",
                                                                                                 "textAlign": "center",
                                                                                                 "padding": "20px"})

    # Generación del gráfico de rigidez dinámica
    try:
        if fK.size > 0 and S_ff.size > 0 and magK.size > 0 and phaseK.size > 0:
            if not (np.isfinite(fK).any() and np.isfinite(S_ff).any() and np.isfinite(magK).any() and np.isfinite(phaseK).any()):
                raise ValueError("Arrays contienen solo valores no finitos")
            umbral_Sff = max(CONFIG.UMBRALES_DATOS['MIN_AMPLITUD_RUIDO'], CONFIG.UMBRALES_DATOS['FACTOR_UMBRAL_SFF'] * np.max(S_ff[np.isfinite(S_ff)]))
            mask = (fK >= CONFIG.LIMITES_FISICOS['FREQ_MIN']) & (S_ff > umbral_Sff) & np.isfinite(fK) & np.isfinite(S_ff)
            if not np.any(mask):
                raise ValueError("No hay datos válidos después de filtrar")
            f_plot = fK[mask]
            mag_plot = magK[mask]
            phase_plot = phaseK[mask]
            if len(f_plot) == 0 or not np.isfinite(mag_plot).any():
                raise ValueError("Sin datos válidos para graficar")
            from dynamic_stiffness_analyzer.visualization.stiffness_plot import generar_grafico_rigidez
            fig_disp = generar_grafico_rigidez(f_plot, mag_plot, phase_plot, seleccion_eje, escala_x, escala_y)
        else:
            raise ValueError("Sin datos válidos para generar gráfico de rigidez")
    except Exception as e:
        print(f"[ERROR] Error generando gráfico de rigidez dinámica: {e}")
        from dynamic_stiffness_analyzer.visualization.shared import generar_figura_vacia
        fig_disp = generar_figura_vacia("Error en gráfico de rigidez dinámica")

######################################################################################################################################
                                                    # --- Gráfico de coherencia ROBUSTO ---

    try:
        from dynamic_stiffness_analyzer.visualization.coherence_plot import generar_grafico_coherencia
        fig_coherencia = generar_grafico_coherencia(fK, S_ff if 'S_ff' in locals() else np.array([]), S_xx if 'S_xx' in locals() else np.array([]), S_xf if 'S_xf' in locals() else np.array([]))
    except Exception as e:
        print(f"[ERROR] Error generando gráfico de coherencia: {e}")
        from dynamic_stiffness_analyzer.visualization.shared import generar_figura_vacia
        fig_coherencia = generar_figura_vacia("Error en gráfico de coherencia")

    # Retorno final con manejo de errores
    try:
        return (fig_tiempo, fig_fft, fig_waterfall, fig_damping, fig_disp, fig_coherencia, curvas_enfasis, opciones_curvas,
                estado_fijar_vista, estilo_fijar, mediana_val, highpass_val, bandpass_multibanda)
    except Exception as e:
        print(f"[ERROR CRÍTICO] Error en retorno final: {e}")
        from dynamic_stiffness_analyzer.visualization.shared import generar_graficos_vacios
        return generar_graficos_vacios()

######################################################################################################################################
                                            # --- (Amortiguamiento extraído a analysis/damping.py) ---

######################################################################################################################################
                                            # --- Optimizaciones para datasheets grandes ---

# Estas funciones mejoran el rendimiento sin tocar el código existente
def optimizar_dataframe_para_visualizacion(df, max_puntos=50000):
    """
    Función simple que reduce puntos SOLO para visualización, sin tocar lógica existente.
    Preserva la calidad de datos manteniendo características importantes.
    """
    if df is None or len(df) <= max_puntos:
        return df, False

    # Muestreo inteligente: más denso al inicio (impactos) y espaciado después
    n_total = len(df)
    step = n_total // max_puntos

    # 30% de puntos en el primer 10% del tiempo (para capturar impactos)
    primer_10_pct = n_total // 10
    puntos_inicio = int(max_puntos * 0.3)
    step_inicio = max(1, primer_10_pct // puntos_inicio)

    # 70% restante distribuido uniformemente
    puntos_resto = max_puntos - puntos_inicio
    step_resto = max(1, (n_total - primer_10_pct) // puntos_resto)
    indices = []

    # Índices del inicio (alta densidad)
    indices.extend(range(0, primer_10_pct, step_inicio))

    # Índices del resto (densidad normal)
    indices.extend(range(primer_10_pct, n_total, step_resto))

    # Eliminar duplicados y ordenar
    indices = sorted(list(set(indices)))

    # Asegurar que siempre incluimos el último punto
    if indices[-1] != n_total - 1:
        indices.append(n_total - 1)
    return df.iloc[indices].copy().reset_index(drop=True), True

def mostrar_progreso_simple(mensaje, puntos_totales, puntos_finales=None):

    # Muestra información simple de progreso en consola.
    if puntos_finales:
        reduccion = ((puntos_totales - puntos_finales) / puntos_totales) * 100
        print(f"[OPTIMIZACIÓN] {mensaje} - {puntos_totales:,} → {puntos_finales:,} puntos ({reduccion:.1f}% reducción)")
    else:
        print(f"[PROGRESO] {mensaje} - Procesando {puntos_totales:,} puntos")

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                                # -- Sistema de caché computacional (servicio global) --
from dynamic_stiffness_analyzer.services.cache import CACHE as cache_computacional

def generar_grafico_tiempo_optimizado(df, seleccion_multi, df_original=None, filtro_aplicado=False, df_corte_json=None):
    """
    Versión optimizada del gráfico de tiempo que mantiene toda la lógica original.
    Solo optimiza la visualización para datasets grandes.
    """

    # Optimizar SOLO si el dataset es grande
    df_viz, optimizado = optimizar_dataframe_para_visualizacion(df, max_puntos=20000)
    if optimizado:
        mostrar_progreso_simple("Gráfico de tiempo", len(df), len(df_viz))

    # Usar exactamente la misma lógica del gráfico original
    fig_tiempo = go.Figure()
    t = df_viz['tiempo'].values
    colores = ['#1f77b4',
               '#ff7f0e',
               '#2ca02c',
               '#d62728',
               '#9467bd',
               '#8c564b',
               '#e377c2',
               '#7f7f7f',
               '#bcbd22',
               '#17becf']
    for i, col in enumerate(seleccion_multi):
        color = colores[i % len(colores)]

        # Mostrar original si hay filtro aplicado
        if filtro_aplicado and df_original is not None and col in df_original.columns and not df_corte_json:
            df_orig_viz, _ = optimizar_dataframe_para_visualizacion(df_original, max_puntos=20000)
            fig_tiempo.add_trace(go.Scatter(x=df_orig_viz['tiempo'].values, y=df_orig_viz[col].values, mode='lines',
                                            name=col + '(original)', line=dict(dash='dot', color='gray')))

        # Mostrar la señal actual
        if col in df_viz.columns:
            nombre = col + (' (filtrada)' if filtro_aplicado else '')
            fig_tiempo.add_trace(go.Scatter(x=t, y=df_viz[col].values, mode='lines', name=nombre,
                                            line=dict(color=color)))

    # Añadir info de optimización solo si se aplicó
    titulo = 'Dominio del Tiempo'
    if optimizado:
        titulo += f' (Visualización optimizada: {len(df_viz):,}/{len(df):,} puntos)'
    fig_tiempo.update_layout(title=titulo, xaxis_title='Tiempo (s)', yaxis_title='Amplitud (g)',
                             paper_bgcolor='#111111',
                             plot_bgcolor='#111111', font=dict(color='white'))
    return fig_tiempo

def generar_grafico_fft_optimizado(df, seleccion_multi, escala_x, escala_y):
    fig_fft = go.Figure()
    if df is None or df.empty:
        return fig_fft
    t = df['tiempo'].values

    # cálculo dt y fs
    if len(t) < 2:
        print("[WARNING] Insuficientes puntos de tiempo para FFT")
        return fig_fft
    dt_values = np.diff(t)
    dt_values_valid = dt_values[dt_values > 0]
    if len(dt_values_valid) == 0:
        print("[ERROR] No hay intervalos de tiempo válidos para FFT")
        return fig_fft
    dt = np.median(dt_values_valid)
    if dt <= 0 or not np.isfinite(dt):

        # Fallback: calcular desde rango total
        dt = (t[-1] - t[0]) / (len(t) - 1) if len(t) > 1 else 0.001
        if dt <= 0:
            print("[WARNING] dt inválido en FFT - usando valor por defecto")
            dt = 0.001  # 1ms por defecto
    fs = 1 / dt
    print(f"[DEBUG] FFT - dt={dt:.6f}, fs={fs:.2f} Hz")
    print(f"[DEBUG] FFT usa TODOS los {len(df):,} puntos disponibles (sin limitación)")
    for col in seleccion_multi:
        if col not in df.columns:
            continue
        y = df[col].values

        # Validar que la señal no esté vacía o sea toda NaN
        if len(y) == 0 or not np.isfinite(y).any():
            print(f"[WARNING] Saltando columna {col}: datos inválidos para FFT")
            continue
        print(f"[DEBUG] Procesando columna: {col}")
        try:

            # Ventaneo exponencial para análisis correcto de aceleración
            if col.startswith('accel_'):
                print(f"[DEBUG] REACTIVANDO ventana exponencial para {col}")
                y_proc = ventana_exponencial(y, fs)

                # y_proc = y  # <- Línea comentada para mantener la ventana exponencial

            elif col.startswith('fuerza'):
                y_proc = ventana_fuerza_adaptativa(y, fs)
            else:
                y_proc = y
        except Exception as e:
            print(f"[WARNING] Error en ventaneo para {col}: {e}")
            y_proc = y
        N = len(y_proc)
        if N < 4:  # Mínimo para FFT
            print(f"[WARNING] Insuficientes puntos para FFT en {col}: {N}")
            continue
        try:
            yf = rfft(y_proc * get_window('hann', N))
            xf = rfftfreq(N, dt)
            amp = np.abs(yf)

            # Validar que FFT es utilizable
            if not np.isfinite(amp).any() or not np.isfinite(xf).any():
                print(f"[WARNING] FFT inválida para {col}")
                continue
            if escala_y == 'db':
                amp = 20 * np.log10(np.maximum(amp, 1e-12))

                # Filtrar valores infinitos
                amp = np.where(np.isfinite(amp), amp, -240)

            # Optimización visual centralizada
            if len(xf) > CONFIG.VISUALIZACION['MAX_PUNTOS_FFT']:

                # Reducir solo visualmente, preservando características importantes
                step_visual = max(1, len(xf) // CONFIG.VISUALIZACION['REDUCCION_VISUAL_FFT'])
                xf_visual = xf[::step_visual]
                amp_visual = amp[::step_visual]
                print(f"[DEBUG] FFT visual: {len(xf)} → {len(xf_visual)} puntos (preserva resolución hasta {xf[-1]:.0f} Hz)")
            else:
                xf_visual = xf
                amp_visual = amp
                print(f"[DEBUG] FFT completa: {len(xf)} puntos hasta {xf[-1]:.0f} Hz")
            fig_fft.add_trace(go.Scatter(x=xf_visual, y=amp_visual, mode='lines', name=col))
        except Exception as e:
            print(f"[ERROR] Error en FFT para {col}: {e}")
            continue

    # Título con rango real
    titulo = f'Dominio de la Frecuencia (FFT) (Optimizada para {len(df):,} puntos) - fs={fs:.1f} Hz'
    fig_fft.update_layout(title=titulo, xaxis_title='Frecuencia (Hz)',
                          yaxis_title='Amplitud (dB)' if escala_y == 'db' else 'Amplitud (g)', xaxis_type=escala_x,
                          paper_bgcolor='#111111', plot_bgcolor='#111111', font=dict(color='white'))
    return fig_fft

def generar_waterfall_optimizado(df_json, seleccion_eje, escala_x, escala_y, curvas_enfasis, estado_fijar_vista,
                                 duracion_segmento=None):
    """
    Versión optimizada del gráfico 3D waterfall que detecta automáticamente si necesita optimización.
    Adapta la resolución según el tamaño del dataset para mantener el rendimiento.
    """
    try:
        if df_json is None or df_json == '':
            print("[WARNING] df_json vacío en waterfall")
            return go.Figure(), []
        df_actual = pd.read_json(df_json, orient='split')
        if df_actual.empty or seleccion_eje not in df_actual.columns:
            print(f"[WARNING] DataFrame vacío o columna {seleccion_eje} no encontrada")
            return go.Figure(), []
        t = df_actual['tiempo'].values
        y_wf = df_actual[seleccion_eje].values

        # Validación de datos básicos
        if len(t) < 2 or len(y_wf) < 2:
            print("[WARNING] Insuficientes datos para waterfall")
            return go.Figure(), []

        # Cálculo robusto de dt y fs
        dt_values = np.diff(t)
        dt_valid = dt_values[dt_values > 0]
        if len(dt_valid) == 0:
            dt = 0.001  # fallback
        else:
            dt = np.median(dt_valid)
            if dt <= 0 or not np.isfinite(dt):
                dt = (t[-1] - t[0]) / (len(t) - 1) if len(t) > 1 else 0.001
        fs = 1 / dt
        N = len(y_wf)
        nyquist_freq = fs / 2  # Añadido para evitar error de variable no definida
        print(f"[DEBUG] Waterfall - N={N}, dt={dt:.6f}, fs={fs:.2f}")

        # Lógica restaurada: el usuario controla window_len por input, solo se fuerza el mínimo físico
        min_window = CONFIG.TOLERANCIAS['MIN_DURACION_SEGMENTO']
        if duracion_segmento is not None and duracion_segmento > 0:
            window_len = int(max(duracion_segmento, min_window) * fs)
        else:
            window_len = int(min_window * fs)

        # No limitar artificialmente el máximo, solo por tamaño de datos
        window_len = min(window_len, N)
        overlap = 0.5
        step = max(1, int(window_len * (1 - overlap)))
        segment_starts = list(range(0, N - window_len + 1, step))

        # Limitar segmentos para rendimiento
        if len(segment_starts) > CONFIG.UMBRALES_DATOS['MAX_SEGMENTOS']:
            indices = np.linspace(0, len(segment_starts) - 1, CONFIG.UMBRALES_DATOS['MAX_SEGMENTOS'], dtype=int)
            segment_starts = [segment_starts[i] for i in indices]

        # Debug: número de segmentos y eje de tiempo
        print(f"[DEBUG] Número de segmentos: {len(segment_starts)}")
        print(f"[DEBUG] Duración de cada segmento: {window_len/fs:.2f} s")
        print(f"[DEBUG] Eje de tiempo waterfall: {[round((t[start] + t[min(start + window_len, N)-1]) / 2, 2) for start in segment_starts]}")

        # Procesamiento de segmentos
        segments_data = []
        fig_waterfall = go.Figure()
        for i, start in enumerate(segment_starts):
            end = min(start + window_len, N)
            actual_len = end - start
            if actual_len < min_window:
                continue

            # Extraer segmento y aplicar ventana
            seg = y_wf[start:end]
            window = get_window('hann', actual_len)
            seg_windowed = seg * window

            # FFT del segmento
            Z = np.abs(rfft(seg_windowed))
            freqs = rfftfreq(actual_len, dt)

            # Validación de FFT
            if not np.isfinite(Z).any() or len(Z) == 0:
                continue

            # Aplicar escala Y
            if escala_y == 'db':
                Z_plot = 20 * np.log10(np.maximum(Z, 1e-12))
            else:
                Z_plot = Z

            # Tiempo central del segmento
            tiempo_central = t[start + actual_len // 2]

            # Usar todo el rango sin limites
            freqs_plot = freqs  # Todo el rango de 0 a fs/2
            Z_plot_reduced = Z_plot  # Todas las amplitudes

            # Debug del primer segmento
            if i == 0:
                print(f"[DEBUG] Rango frecuencias segmento 1: {freqs_plot[0]:.2f} - {freqs_plot[-1]:.2f} Hz ({len(freqs_plot)} puntos)")
                print(f"[DEBUG] Frecuencia máxima teórica (Nyquist): {fs / 2:.2f} Hz")

            # Determinar estilo según énfasis
            if not curvas_enfasis or str(i) in curvas_enfasis:
                line_width = 6
                opacity = 1.0
            else:
                line_width = 1
                opacity = 0.08

            # Añadir traza 3D (convertir arrays a listas para Plotly)
            fig_waterfall.add_trace(go.Scatter3d(x=list(freqs_plot),
                                                 y=[float(tiempo_central)] * len(freqs_plot),
                                                 z=list(Z_plot_reduced),
                                                 mode='lines',
                                                 line=dict(color=list(Z_plot_reduced), colorscale=[[0.0, 'blue'],
                                                                                                   [0.2, 'deepskyblue'],
                                                                                                   [0.4, 'green'],
                                                                                                   [0.6, 'yellow'],
                                                                                                   [0.8, 'orange'],
                                                                                                   [1.0, 'red']],
                                                           width=line_width),
                                                 opacity=opacity,
                                                 showlegend=False))

            # Datos para exportación (reducir solo para archivo de salida)
            step_export = max(1, len(freqs_plot) // 1000)
            for j in range(0, len(freqs_plot), step_export):
                f, z = freqs_plot[j], Z_plot_reduced[j]
                if np.isfinite(f) and np.isfinite(z):
                    segments_data.append({'segmento': i + 1,
                                          'tiempo_central': tiempo_central,
                                          'frecuencia': f,
                                          'amplitud': z})

        # Configuración de cámara ortogonal perfectamente centrada y sin rotación para vista fijada
        if estado_fijar_vista:
            camera = dict(eye=dict(x=0, y=2.5, z=0),  # Vista cenital, eje Y arriba
                          up=dict(x=0, y=0, z=1),     # Z es arriba en pantalla
                          center=dict(x=0, y=0, z=0),
                          projection=dict(type="orthographic"))
            fig_waterfall.update_layout(title="Waterfall 2D (Vista fijada)",
                                        scene=dict(xaxis_title='Frecuencia (Hz)',
                                                   yaxis_title='Tiempo (s)',
                                                   zaxis_title='Amplitud (g)' if escala_y != 'db' else 'Amplitud (dB)',
                                                   xaxis=dict(color='white', backgroundcolor='#111111', showbackground=True),
                                                   yaxis=dict(color='white', backgroundcolor='#111111', showbackground=True),
                                                   zaxis=dict(color='white', backgroundcolor='#111111', showbackground=True),
                                                   camera=camera),
                                        paper_bgcolor='#111111',
                                        font=dict(color='white'))
        else:
            camera = dict(eye=dict(x=1.2, y=1.2, z=0.8),
                          up=dict(x=0, y=0, z=1),
                          center=dict(x=0, y=0, z=0),
                          projection=dict(type="perspective"))
            scene_config = dict(xaxis=dict(title="Frecuencia (Hz)",
                                           type=escala_x,
                                           color='white',
                                           backgroundcolor='black',  
                                           gridcolor='white',        
                                           showbackground=True,
                                           showgrid=True,
                                           zeroline=True,
                                           zerolinecolor='white'),
                               yaxis=dict(title="Tiempo (s)",
                                          color='white',
                                          backgroundcolor='black',  
                                          gridcolor='white',        
                                          showbackground=True,
                                          showgrid=True,
                                          zeroline=True,
                                          zerolinecolor='white'),
                               zaxis=dict(title="Amplitud" + (" (dB)" if escala_y == 'db' else " (g)"),
                                          color='white',
                                          backgroundcolor='black', 
                                          gridcolor='white',        
                                          showbackground=True,
                                          showgrid=True,
                                          zeroline=True,
                                          zerolinecolor='white'),
                               camera=camera)
            titulo = f'Waterfall 3D - Rango: 0-{nyquist_freq:.0f} Hz ({len(segment_starts)} segmentos) - fs={fs:.0f} Hz'
            fig_waterfall.update_layout(title=dict(text=titulo, font=dict(color='white', size=16)), scene=scene_config,
                                        paper_bgcolor='#111111', plot_bgcolor='black',  # Fondo negro
                                        font=dict(color='white'), margin=dict(l=0, r=0, t=50, b=0))
        print(f"[DEBUG] Waterfall completado: {len(segment_starts)} segmentos, {len(segments_data)} puntos")
        return fig_waterfall, segments_data
    except Exception as e:
        print(f"[ERROR] Error crítico en waterfall: {e}")
        traceback.print_exc()
        fig_vacio = go.Figure()
        fig_vacio.update_layout(title=f"Error en Waterfall: {str(e)[:50]}",
                                paper_bgcolor='#111111',
                                plot_bgcolor='#111111',
                                font=dict(color='white'))
        return fig_vacio, []

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                            # --- Funciones con caché para FFT y waterfall ---

def generar_grafico_fft_con_cache(df, seleccion_multi, escala_x, escala_y):
    """
    Versión con caché de la función FFT que evita recálculos innecesarios.
    Conserva toda la funcionalidad original pero optimiza el rendimiento.
    """
    global cache_computacional

    # Generar hash de los parámetros para verificar si ya se calculó
    try:

        # Crear identificador único de los datos y parámetros
        data_hash = None
        if df is not None and not df.empty:

            # Usar una muestra de los datos para el hash (más eficiente)
            sample_data = df.iloc[::max(1, len(df) // 1000)].to_string()  # Muestra cada 1000 puntos
            params = f"{sample_data}_{seleccion_multi}_{escala_x}_{escala_y}"
            data_hash = cache_computacional.generar_hash_parametros(params)

        # Intentar obtener del caché
        if data_hash:
            resultado_cache = cache_computacional.obtener_de_cache(data_hash)
            if resultado_cache is not None:
                print(
                    f"[CACHE] FFT obtenida del caché (hit rate: {cache_computacional.estadisticas_cache()['hit_rate']:.1f}%)")
                return resultado_cache

        # Si no está en caché, calcular usando la función original
        print("[CACHE] Calculando nueva FFT...")
        resultado = generar_grafico_fft_optimizado(df, seleccion_multi, escala_x, escala_y)

        # Guardar en caché
        if data_hash:
            cache_computacional.guardar_en_cache(data_hash, resultado)
        return resultado
    except Exception as e:
        print(f"[CACHE] Error en caché FFT, usando función original: {e}")
        return generar_grafico_fft_optimizado(df, seleccion_multi, escala_x, escala_y)

def generar_waterfall_con_cache(df_json, seleccion_eje, escala_x, escala_y, curvas_enfasis, estado_fijar_vista,
                                duracion_segmento=None):
    """
    Versión con caché de la función waterfall que evita recálculos de segmentos.
    Conserva toda la funcionalidad original pero optimiza el rendimiento.
    """
    global cache_computacional

    # Generar hash de los parámetros para verificar si ya se calculó
    try:

        # Crear identificador único de los datos y parámetros
        data_hash = None
        if df_json and df_json != '':

            # Usar hash del JSON y parámetros
            params = f"{df_json[:1000]}_{seleccion_eje}_{escala_x}_{escala_y}_{curvas_enfasis}_{estado_fijar_vista}_{duracion_segmento}"
            data_hash = cache_computacional.generar_hash_parametros(params)

        # Intentar obtener del caché
        if data_hash:
            resultado_cache = cache_computacional.obtener_de_cache(data_hash)
            if resultado_cache is not None:
                print(
                    f"[CACHE] Waterfall obtenido del caché (hit rate: {cache_computacional.estadisticas_cache()['hit_rate']:.1f}%)")
                return resultado_cache

        # Si no está en caché, calcular usando la función original
        print("[CACHE] Calculando nuevo waterfall...")
        resultado = generar_waterfall_optimizado(df_json, seleccion_eje, escala_x, escala_y, curvas_enfasis, estado_fijar_vista,
                                                 duracion_segmento)

        # Guardar en caché
        if data_hash:
            cache_computacional.guardar_en_cache(data_hash, resultado)
        return resultado
    except Exception as e:
        print(f"[CACHE] Error en caché waterfall, usando función original: {e}")
        return generar_waterfall_optimizado(df_json, seleccion_eje, escala_x, escala_y, curvas_enfasis, estado_fijar_vista,
                                            duracion_segmento)

def limpiar_cache_si_necesario(forzar=False):
    # Limpia el caché cuando sea necesario para liberar memoria.
    try:
        stats = cache_computacional.estadisticas_cache()
        if forzar or stats['cache_size'] >= cache_computacional.max_cache_size * 0.9:
            cache_computacional.limpiar_cache()
            print(f"[CACHE] Caché limpiado. Estadísticas previas: {stats}")
            return True
        if stats['hits'] + stats['misses'] > 0:
            print(f"[CACHE] Stats: {stats['hits']} hits, {stats['misses']} misses, {stats['hit_rate']:.1f}% hit rate, {stats['cache_size']} entradas")
        return False
    except Exception as e:
        print(f"[CACHE] Error al limpiar caché: {e}")
        return False

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                                # --- Funciones para caché ---

def generar_grafico_fft_adaptativo(df, seleccion_multi, escala_x, escala_y):
    """
    Función adaptativa que usa caché si está habilitado, sino usa la función original.
    Esta función puede reemplazar las llamadas existentes sin romper funcionalidad.
    """
    global USAR_CACHE
    if USAR_CACHE:
        return generar_grafico_fft_con_cache(df, seleccion_multi, escala_x, escala_y)
    else:
        return generar_grafico_fft_optimizado(df, seleccion_multi, escala_x, escala_y)

def generar_waterfall_adaptativo(df_json, seleccion_eje, escala_x, escala_y, curvas_enfasis, estado_fijar_vista,
                                 duracion_segmento=None):
    
    # Función waterfall 3D original sin complicaciones innecesarias
    print("[DEBUG] *** WATERFALL 3D GENERALIZADO - RANGO COMPLETO DE FRECUENCIAS ***")
    try:
        if df_json is None or df_json == '':
            return go.Figure(), []
        df_actual = pd.read_json(df_json, orient='split')
        if df_actual.empty or seleccion_eje not in df_actual.columns:
            return go.Figure(), []
        t = df_actual['tiempo'].values
        y_wf = df_actual[seleccion_eje].values
        if len(t) < 2 or len(y_wf) < 2:
            return go.Figure(), []
        dt_values = np.diff(t)
        dt_valid = dt_values[dt_values > 0]
        if len(dt_valid) == 0:
            dt = 0.001
        else:
            dt_median = np.median(dt_valid)
            if dt_median <= 0 or not np.isfinite(dt_median):
                dt = (t[-1] - t[0]) / (len(t) - 1) if len(t) > 1 else 0.001
            else:
                dt = dt_median

        # logica de corrección temporal
        dt_mean = np.mean(dt_valid) if len(dt_valid) > 0 else dt
        dt_std = np.std(dt_valid) if len(dt_valid) > 0 else 0
        irregularidad_relativa = dt_std / dt_mean if dt_mean > 0 else 0.0

        # Si hay irregularidad > 5%, recalcular dt
        if irregularidad_relativa > 0.05:
            print(f"[DEBUG] Waterfall detecta irregularidad temporal: {irregularidad_relativa*100:.2f}%")

            # Usar el mismo dt que el del analisis principal
            dt_corregido = (t[-1] - t[0]) / (len(t) - 1) if len(t) > 1 else dt
            dt = dt_corregido
            print(f"[DEBUG] Waterfall dt corregido: {dt:.6f} s")
        fs = 1 / dt
        N = len(y_wf)
        nyquist_freq = fs / 2
        print(f"[DEBUG] Waterfall corregido - N={N}, dt={dt:.6f}, fs={fs:.2f} Hz, Nyquist={nyquist_freq:.2f} Hz")

        # Segmentación para garantizar rango completo

        # Lógica restaurada: el usuario controla window_len por input, solo se fuerza el mínimo físico
        min_window = CONFIG.TOLERANCIAS['MIN_DURACION_SEGMENTO']
        if duracion_segmento is not None and duracion_segmento > 0:
            window_len = int(max(duracion_segmento, min_window) * fs)
        else:
            window_len = int(min_window * fs)
        # No limitar artificialmente el máximo, solo por tamaño de datos
        window_len = min(window_len, N)
        overlap = 0.5
        step = max(1, int(window_len * (1 - overlap)))
        segment_starts = list(range(0, N - window_len + 1, step))
        # Limitar segmentos para rendimiento
        if len(segment_starts) > CONFIG.UMBRALES_DATOS['MAX_SEGMENTOS']:
            indices = np.linspace(0, len(segment_starts) - 1, CONFIG.UMBRALES_DATOS['MAX_SEGMENTOS'], dtype=int)
            segment_starts = [segment_starts[i] for i in indices]

        # Debug: número de segmentos y eje de tiempo
        print(f"[DEBUG] Número de segmentos: {len(segment_starts)}")
        print(f"[DEBUG] Duración de cada segmento: {window_len/fs:.2f} s")
        print(f"[DEBUG] Eje de tiempo waterfall: {[round((t[start] + t[min(start + window_len, N)-1]) / 2, 2) for start in segment_starts]}")

        # Procesamiento de segmentos
        segments_data = []
        fig_waterfall = go.Figure()
        for i, start in enumerate(segment_starts):
            end = min(start + window_len, N)
            actual_len = end - start
            if actual_len < 512:  # Mínimo más alto
                continue

            # Extraer segmento
            seg = y_wf[start:end]
            tiempo_central = (t[start] + t[end-1]) / 2

            # Aplicar ventana Hann
            window = get_window('hann', actual_len)
            seg_windowed = seg * window

            # FFT
            Z_complex = rfft(seg_windowed)
            Z_magnitude = np.abs(Z_complex)
            freqs = rfftfreq(actual_len, dt)
            if not np.isfinite(Z_magnitude).any() or len(Z_magnitude) == 0:
                continue

            # Debug del primer segmento para verificar rango
            if i == 0:
                print(f"[DEBUG] *** VERIFICACIÓN RANGO PRIMER SEGMENTO ***")
                print(f"[DEBUG] Longitud segmento: {actual_len} puntos")
                print(f"[DEBUG] dt utilizado: {dt:.6f} s")
                print(f"[DEBUG] fs calculado: {fs:.2f} Hz")
                print(f"[DEBUG] Nyquist teórico: {nyquist_freq:.2f} Hz")
                print(f"[DEBUG] Frecuencia mínima FFT: {freqs[0]:.2f} Hz")
                print(f"[DEBUG] Frecuencia máxima FFT: {freqs[-1]:.2f} Hz")
                print(f"[DEBUG] Puntos de frecuencia: {len(freqs)}")
                print(f"[DEBUG] Resolución frecuencial: {freqs[1] - freqs[0]:.2f} Hz")

            # Escala Y
            if escala_y == 'db':
                Z_plot = 20 * np.log10(np.maximum(Z_magnitude, 1e-12))
            else:
                Z_plot = Z_magnitude

            # USAR TODO EL RANGO
            freqs_plot = freqs  # 0 Hz hasta fs/2 COMPLETO
            Z_plot_final = Z_plot  # TODAS las amplitudes

            # Debug del rango final
            if i == 0:
                print(f"[DEBUG] *** RANGO FINAL PARA GRÁFICO ***")
                print(f"[DEBUG] freqs_plot mín: {freqs_plot[0]:.2f} Hz")
                print(f"[DEBUG] freqs_plot máx: {freqs_plot[-1]:.2f} Hz")
                print(f"[DEBUG] Puntos en gráfico: {len(freqs_plot)}")
                print(f"[DEBUG] ¿Llega hasta Nyquist?: {abs(freqs_plot[-1] - nyquist_freq) < 1.0}")

            # Estilo
            if not curvas_enfasis or str(i) in curvas_enfasis:
                line_width = 6
                opacity = 1.0
            else:
                line_width = 1
                opacity = 0.08

            # *** COLORSCALE GEOLÓGICO CORRECTO ***
            colorscale_geologico = [[0.0, '#000080'],   # (bajas amplitudes)
                                    [0.1, '#0000FF'],   
                                    [0.2, '#0080FF'],   
                                    [0.3, '#00FFFF'],   
                                    [0.4, '#00FF80'],   
                                    [0.5, '#00FF00'],   
                                    [0.6, '#80FF00'],   
                                    [0.7, '#FFFF00'],   
                                    [0.8, '#FF8000'],   
                                    [0.9, '#FF4000'],   
                                    [1.0, '#FF0000']    # (altas amplitudes)
                                   ]

            # Añadir siempre traza 3D, solo cambia la cámara si la vista está fijada
            fig_waterfall.add_trace(go.Scatter3d(
                x=list(freqs_plot),
                y=[float(tiempo_central)] * len(freqs_plot),
                z=list(Z_plot_final),
                mode='lines',
                line=dict(color=list(Z_plot_final), colorscale=colorscale_geologico, width=line_width),
                opacity=opacity,
                showlegend=False))

            # Datos para exportación
            step_export = max(1, len(freqs_plot) // 2000)
            for j in range(0, len(freqs_plot), step_export):
                if j < len(freqs_plot):
                    f, z = freqs_plot[j], Z_plot_final[j]
                    if np.isfinite(f) and np.isfinite(z):
                        segments_data.append({'segmento': i + 1,
                                              'tiempo_central': tiempo_central,
                                              'frecuencia': f,
                                              'amplitud': z})
        # Configuración de cámara ortogonal para vista fijada, manteniendo títulos de ejes coherentes con los datos
        if estado_fijar_vista:
            camera = dict(eye=dict(x=2.5, y=0, z=0),  # Vista cenital, eje Y arriba
                          up=dict(x=0, y=0, z=1),     # Z es arriba en pantalla
                          center=dict(x=0, y=0, z=0),
                          projection=dict(type="orthographic"))
            fig_waterfall.update_layout(
                title="Waterfall 2D (Vista fijada)",
                scene=dict(xaxis_title='Frecuencia (Hz)',
                           yaxis_title='Tiempo (s)',
                           zaxis_title='Amplitud (g)',
                           xaxis=dict(color='white', backgroundcolor='#111111', showbackground=True),
                           yaxis=dict(color='white', backgroundcolor='#111111', showbackground=True),
                           zaxis=dict(color='white', backgroundcolor='#111111', showbackground=True),
                           camera=camera),
                paper_bgcolor='#111111',
                font=dict(color='white'))
        else:
            camera = dict(eye=dict(x=1.2, y=1.2, z=0.8),
                          up=dict(x=0, y=0, z=1),
                          center=dict(x=0, y=0, z=0),
                          projection=dict(type="perspective"))
            scene_config = dict(xaxis=dict(title="Frecuencia (Hz)",
                                           type=escala_x,
                                           color='white',
                                           backgroundcolor='black',  
                                           gridcolor='white',        
                                           showbackground=True,
                                           showgrid=True,
                                           zeroline=True,
                                           zerolinecolor='white'),
                               yaxis=dict(title="Tiempo (s)",
                                          color='white',
                                          backgroundcolor='black',  
                                          gridcolor='white',        
                                          showbackground=True,
                                          showgrid=True,
                                          zeroline=True,
                                          zerolinecolor='white'),
                               zaxis=dict(title="Amplitud" + (" (dB)" if escala_y == 'db' else " (g)"),
                                          color='white',
                                          backgroundcolor='black', 
                                          gridcolor='white',        
                                          showbackground=True,
                                          showgrid=True,
                                          zeroline=True,
                                          zerolinecolor='white'),
                               camera=camera)
            titulo = f'Waterfall 3D - Rango: 0-{nyquist_freq:.0f} Hz ({len(segment_starts)} segmentos) - fs={fs:.0f} Hz'
            fig_waterfall.update_layout(title=dict(text=titulo, font=dict(color='white', size=16)), scene=scene_config,
                                       paper_bgcolor='#111111', plot_bgcolor='black',  # Fondo negro
                                       font=dict(color='white'), margin=dict(l=0, r=0, t=50, b=0))
        print(f"[DEBUG] *** WATERFALL COMPLETADO ***")
        print(f"[DEBUG] ✅ Segmentos: {len(segment_starts)}")
        print(f"[DEBUG] ✅ Rango real mostrado: 0 - {nyquist_freq:.0f} Hz (fs={fs:.0f} Hz)")
        print(f"[DEBUG] ✅ Colorscale geológico aplicado")
        print(f"[DEBUG] ✅ Grid negro con líneas blancas")
        print(f"[DEBUG] ✅ Waterfall completado: {len(segments_data)} segmentos, máx freq real: {nyquist_freq:.0f} Hz")
        return fig_waterfall, segments_data
    except Exception as e:
        print(f"[ERROR] Error en waterfall: {e}")
        fig_vacio = go.Figure()
        fig_vacio.update_layout(
            title=f"Error: {str(e)[:50]}",
            paper_bgcolor='#111111',
            font=dict(color='white'))
        return fig_vacio, []

def habilitar_cache():
    # Habilita el sistema de caché para mejor rendimiento
    global USAR_CACHE
    USAR_CACHE = True
    print("[CACHE] Sistema de caché habilitado")

def deshabilitar_cache():
    # Deshabilita el sistema de caché y limpia el caché actual
    global USAR_CACHE
    USAR_CACHE = False
    cache_computacional.limpiar_cache()
    print("[CACHE] Sistema de caché deshabilitado y limpiado")

def toggle_cache():
    """Alterna el estado del sistema de caché"""
    global USAR_CACHE
    if USAR_CACHE:
        deshabilitar_cache()
    else:
        habilitar_cache()
    return USAR_CACHE

# Función auxiliar para generar figuras vacías en casos de error
def generar_graficos_vacios():

    # Genera figuras vacías para devolver en caso de error o datos insuficientes
    fig_vacio = go.Figure()
    fig_vacio.update_layout(title="Sin datos disponibles", paper_bgcolor='#111111', plot_bgcolor='#111111',
                            font=dict(color='white'))
    print("[ERROR] Retornando gráficos vacíos por error o falta de datos")
    
    # No mostrar mensajes de error en la interfaz
    return (fig_vacio, fig_vacio, fig_vacio, html.Div(),
            fig_vacio, fig_vacio, [], [], False, {'backgroundColor': '#7C8085',
                                                  'color': 'white',
                                                  'fontWeight': 'bold',
                                                  'borderRadius': '4px',
                                                  'border': 'none',
                                                  'padding': '8px 15px'},
            5, 0.5, '')

def generar_figura_vacia(titulo="Sin datos"):
    """Genera una figura vacía con título personalizado"""
    fig = go.Figure()
    print(f"[ERROR] {titulo}")
    fig.update_layout(title="Sin datos disponibles",
                      paper_bgcolor='#111111',
                      plot_bgcolor='#111111',
                      font=dict(color='white'))
    return fig

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
                                                        # --- Main ---

if __name__ == '__main__':

    # Limpiar caché automáticamente al iniciar la aplicación
    print("[INICIO] Limpiando caché residual...")
    cache_computacional.limpiar_cache()

    # forzar limpieza de memoria Python para asegurar que las correcciones tomen efecto
    gc.collect()
    print("[INICIO] Limpieza de memoria forzada - todas las correcciones aplicadas")

    # Confirmar estado del sistema de caché
    estado_cache = "HABILITADO" if USAR_CACHE else "DESHABILITADO"
    print(f"[CACHÉ] Sistema de caché: {estado_cache}")

    if USAR_CACHE:
        print("[CACHÉ] Caché activo - FFT y waterfall optimizados")
        print("[CACHÉ] Estadísticas disponibles con: cache_computacional.estadisticas_cache()")
        print("[CACHÉ] Limpieza automática: al iniciar y al cargar nuevos archivos")
    else:
        print("[CACHÉ] Caché deshabilitado - funcionamiento estándar")
        print("[CACHÉ] Para habilitar: cambiar USAR_CACHE = True")

    # Confirmación final del bypass
    print("[WATERFALL] Bypass activo - rango completo 0 Hz a fs/2 garantizado")

    webbrowser.open_new("http://127.0.0.1:8050")
    app.run(debug=False, use_reloader=False)

