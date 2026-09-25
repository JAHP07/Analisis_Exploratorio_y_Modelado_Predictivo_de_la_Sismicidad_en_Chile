"""
Módulo de extracción y procesamiento de datos sísmicos.

Este módulo proporciona funciones para obtener datos sísmicos desde la API del USGS,
transformarlos y limpiarlos para su posterior análisis.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
import os


def obtener_datos_sismos(
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    magnitud_minima: float = 4.0,
    latitud_minima: float = -56.0,
    latitud_maxima: float = -17.0,
    longitud_minima: float = -80.0,
    longitud_maxima: float = -65.0
) -> pd.DataFrame:
    """
    Extrae datos sísmicos desde la API del USGS.
    
    Args:
        fecha_inicio: Fecha de inicio en formato 'YYYY-MM-DD'. Por defecto, hace 365 días.
        fecha_fin: Fecha de fin en formato 'YYYY-MM-DD'. Por defecto, hoy.
        magnitud_minima: Magnitud mínima de los sismos a considerar.
        latitud_minima: Límite sur del área geográfica.
        latitud_maxima: Límite norte del área geográfica.
        longitud_minima: Límite oeste del área geográfica.
        longitud_maxima: Límite este del área geográfica.
    
    Returns:
        DataFrame con los datos sísmicos procesados.
    
    Raises:
        requests.RequestException: Si hay un error en la petición a la API.
    """
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    
    if fecha_inicio is None:
        fecha_inicio = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if fecha_fin is None:
        fecha_fin = datetime.now().strftime('%Y-%m-%d')
    
    params = {
        "format": "geojson",
        "starttime": fecha_inicio,
        "endtime": fecha_fin,
        "minlatitude": latitud_minima,
        "maxlatitude": latitud_maxima,
        "minlongitude": longitud_minima,
        "maxlongitude": longitud_maxima,
        "minmagnitude": magnitud_minima
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    
    lista_sismos = []
    for feature in data.get('features', []):
        props = feature['properties']
        coords = feature['geometry']['coordinates']
        
        lista_sismos.append({
            'lugar': props['place'],
            'magnitud': props['mag'],
            'fecha': pd.to_datetime(props['time'], unit='ms'),
            'longitud': coords[0],
            'latitud': coords[1],
            'profundidad': coords[2]
        })
    
    df = pd.DataFrame(lista_sismos)
    return df


def limpiar_datos_sismos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y prepara los datos sísmicos para el análisis.
    
    Args:
        df: DataFrame con los datos sísmicos crudos.
    
    Returns:
        DataFrame con los datos limpios y procesados.
    """
    df_limpio = df.copy()
    
    df_limpio = df_limpio.dropna(subset=['magnitud', 'latitud', 'longitud', 'profundidad'])
    
    df_limpio = df_limpio[df_limpio['magnitud'] > 0]
    df_limpio = df_limpio[df_limpio['profundidad'] >= 0]
    
    df_limpio = df_limpio.reset_index(drop=True)
    
    return df_limpio


def guardar_dataset_analitico(df: pd.DataFrame, save_path: str) -> pd.DataFrame:
    """
    Guarda una versión analítica del dataset con campos clave para agrupaciones.
    
    Args:
        df: DataFrame con datos sísmicos limpios.
        save_path: Ruta destino para archivo CSV.
    
    Returns:
        DataFrame guardado con columnas seleccionadas.
    """
    df_export = df.copy()
    df_export['fecha'] = pd.to_datetime(df_export['fecha'])
    
    dataset_analitico = pd.DataFrame({
        'magnitud': df_export['magnitud'],
        'fecha': df_export['fecha'].dt.date.astype(str),
        'hora': df_export['fecha'].dt.strftime('%H:%M:%S'),
        'latitud': df_export['latitud'],
        'profundidad_km': df_export['profundidad']
    })
    
    directory = os.path.dirname(save_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    dataset_analitico.to_csv(save_path, index=False)
    
    return dataset_analitico


if __name__ == "__main__":
    df = obtener_datos_sismos()
    print(f"Se obtuvieron {len(df)} registros.")
    print(df.head())
    
    df_limpio = limpiar_datos_sismos(df)
    print(f"\nDespués de limpieza: {len(df_limpio)} registros.")
