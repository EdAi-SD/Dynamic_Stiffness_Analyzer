from __future__ import annotations

import os
import tempfile
import zipfile
from typing import Iterable, List, Optional

import pandas as pd


def exportar_waterfall_a_zip(datos: Optional[Iterable[dict]]) -> Optional[str]:
    """
    Recibe una lista de dicts con claves: 'segmento', 'tiempo_central', 'frecuencia', 'amplitud'.
    Genera dos CSV (formato largo y matriz) y devuelve la ruta de un ZIP temporal con ambos.
    Retorna None si no hay datos.
    """
    if not datos:
        return None

    df_export = pd.DataFrame(list(datos))

    # CSV largo
    temp_long = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    df_export.to_csv(temp_long.name, index=False)
    temp_long.close()

    # CSV matriz (pivot)
    matriz = df_export.pivot_table(index="tiempo_central", columns="frecuencia", values="amplitud")
    matriz = matriz.sort_index(axis=0).sort_index(axis=1)
    matriz.reset_index(inplace=True)
    temp_matrix = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    matriz.to_csv(temp_matrix.name, index=False)
    temp_matrix.close()

    # ZIP con ambos
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    with zipfile.ZipFile(temp_zip.name, "w") as zipf:
        zipf.write(temp_long.name, arcname="datos_3D_long.csv")
        zipf.write(temp_matrix.name, arcname="datos_3D_matriz.csv")

    # Limpiar archivos temporales
    try:
        os.remove(temp_long.name)
        os.remove(temp_matrix.name)
    except Exception:
        pass

    return temp_zip.name


