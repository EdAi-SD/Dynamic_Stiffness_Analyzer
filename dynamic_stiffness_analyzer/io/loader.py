from __future__ import annotations

import base64
import io
import os
import re
import tempfile
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


Columnas = List[str]


def _detectar_separador(linea: str) -> str:
    if "\t" in linea:
        return "\t"
    if linea.count(";") > linea.count(","):
        return ";"
    return ","


def _mapear_columnas_flex(df: pd.DataFrame, columnas_esperadas: Columnas) -> Optional[pd.DataFrame]:
    columnas_mapeo: Dict[str, Columnas] = {
        "tiempo": ["tiempo", "time", "t", "tiempo (s)", "time (s)"],
        "fuerza": ["fuerza", "force", "f", "fuerza (n)", "force (n)"],
        "accel_x": [
            "accel_x",
            "aceleracion_x",
            "acel_x",
            "ax",
            "acc x",
            "aceleracion x",
            "aceleración x",
            "acceleration x",
        ],
        "accel_y": [
            "accel_y",
            "aceleracion_y",
            "acel_y",
            "ay",
            "acc y",
            "aceleracion y",
            "aceleración y",
            "acceleration y",
        ],
        "accel_z": [
            "accel_z",
            "aceleracion_z",
            "acel_z",
            "az",
            "acc z",
            "aceleracion z",
            "aceleración z",
            "acceleration z",
        ],
    }
    columnas_encontradas: Dict[str, str] = {}
    columnas_lower = [c.lower().strip() for c in df.columns]
    for clave, posibles in columnas_mapeo.items():
        for posible in posibles:
            if posible in columnas_lower:
                idx = columnas_lower.index(posible)
                columnas_encontradas[clave] = df.columns[idx]
                break
    if len(columnas_encontradas) >= 3:
        df_estandar = pd.DataFrame()
        for clave in columnas_esperadas:
            if clave in columnas_encontradas:
                df_estandar[clave] = df[columnas_encontradas[clave]]
            else:
                df_estandar[clave] = np.nan
        return df_estandar
    return None


def cargar_contenidos_upload(contents: str, filename: str) -> Tuple[str, Optional[str], str]:
    """
    Procesa el contenido subido (Dash dcc.Upload) y retorna:
    - Mensaje a mostrar en UI
    - DataFrame serializado a JSON (orient='split') o None en caso de error
    - Mensaje de carga (vacío si OK)
    """
    if contents is None:
        return "", None, ""

    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    try:
        decoded_str = decoded.decode("utf-8")
        lineas = decoded_str.splitlines()
        ext = os.path.splitext(filename)[-1].lower()
        columnas_esperadas = ["tiempo", "fuerza", "accel_x", "accel_y", "accel_z"]

        # CSV/XLSX directo
        if ext in [".csv", ".xlsx"]:
            try:
                if ext == ".xlsx":
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                        tmp.write(decoded)
                        tmp_path = tmp.name
                    df = pd.read_excel(tmp_path)
                    os.remove(tmp_path)
                else:
                    sep = _detectar_separador(lineas[0]) if lineas else ","
                    df = pd.read_csv(io.StringIO(decoded_str), sep=sep)

                df_estandar = _mapear_columnas_flex(df, columnas_esperadas)
                if df_estandar is not None:
                    return (
                        f"Archivo cargado: {filename}",
                        df_estandar.to_json(date_format="iso", orient="split"),
                        "",
                    )
                if len(df.columns) >= 5:
                    df_renamed = df.iloc[:, :5].copy()
                    df_renamed.columns = columnas_esperadas
                    return (
                        f"Archivo cargado: {filename}",
                        df_renamed.to_json(date_format="iso", orient="split"),
                        "",
                    )
            except Exception:
                # Fallback a TXT/Catman
                pass

        # TXT Catman o CSV problemático
        idx_canales = None
        nombres_canales: Columnas = []
        for i, linea in enumerate(lineas):
            if re.search(r"(time|acc|fuerza|force)", linea, re.IGNORECASE):
                sep = _detectar_separador(linea)
                nombres_canales = [c.strip() for c in re.split(r"[;,\t]+", linea.strip())]
                idx_canales = i
                break

        def es_linea_datos(linea: str, ncols_min: int = 5) -> bool:
            campos = re.split(r"[;,\t ]+", linea.strip())
            num_ok = 0
            for campo in campos:
                if campo == "":
                    continue
                try:
                    float(campo)
                    num_ok += 1
                except ValueError:
                    break
            return num_ok >= ncols_min

        idx_datos = None
        for i in range((idx_canales + 1) if idx_canales is not None else 0, len(lineas)):
            if es_linea_datos(lineas[i]):
                idx_datos = i
                break

        if idx_canales is not None and idx_datos is not None:
            sep = "\t"
            contenido_limpio = sep.join(nombres_canales) + "\n" + "\n".join(lineas[idx_datos:])
            contenido_limpio = re.sub(r"[ \t]+", "\t", contenido_limpio)
            try:
                df2 = pd.read_csv(io.StringIO(contenido_limpio), sep=sep, engine="python", usecols=range(5))
                df2.columns = columnas_esperadas
                # Limpieza mínima, igual que el monolito
                df2 = df2[pd.to_numeric(df2["tiempo"], errors="coerce").notnull()]
                for col in df2.columns:
                    df2[col] = pd.to_numeric(df2[col], errors="coerce")
                df2 = df2.dropna(subset=["tiempo"])  # tiempo válido
                df2 = df2[df2["tiempo"] >= 0]
                df2 = df2.dropna(subset=["fuerza", "accel_x", "accel_y", "accel_z"], how="all")
                if df2.empty:
                    return "Error: Archivo sin datos válidos tras limpieza.", None, ""
                return (
                    f"Archivo cargado: {filename}",
                    df2.to_json(date_format="iso", orient="split"),
                    "",
                )
            except Exception as e:
                return f"Error procesando datos: {e}", None, ""
        else:
            return "No se encontraron datos válidos en el archivo.", None, ""
    except Exception as e:
        return f"Error al leer el archivo: {e}", None, ""


