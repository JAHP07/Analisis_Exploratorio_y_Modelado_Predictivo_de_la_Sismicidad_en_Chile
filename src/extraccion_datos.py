"""Módulo de extracción y procesamiento de datos sísmicos."""

from datetime import datetime, timedelta

import pandas as pd
import requests

USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
COLUMNAS_REQUERIDAS = [
    "lugar",
    "magnitud",
    "fecha",
    "longitud",
    "latitud",
    "profundidad",
]


def _validar_formato_fecha(fecha: str, nombre_parametro: str) -> datetime:
    """Valida y parsea una fecha con formato YYYY-MM-DD."""
    try:
        return datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(
            f"{nombre_parametro} debe tener formato YYYY-MM-DD. Valor recibido: {fecha}"
        ) from exc


def _validar_rangos_geograficos(
    latitud_minima: float,
    latitud_maxima: float,
    longitud_minima: float,
    longitud_maxima: float,
) -> None:
    """Valida rangos geográficos de latitud y longitud."""
    if latitud_minima >= latitud_maxima:
        raise ValueError("latitud_minima debe ser menor que latitud_maxima.")
    if longitud_minima >= longitud_maxima:
        raise ValueError("longitud_minima debe ser menor que longitud_maxima.")
    if not (-90 <= latitud_minima <= 90 and -90 <= latitud_maxima <= 90):
        raise ValueError("Las latitudes deben estar entre -90 y 90.")
    if not (-180 <= longitud_minima <= 180 and -180 <= longitud_maxima <= 180):
        raise ValueError("Las longitudes deben estar entre -180 y 180.")


def obtener_datos_sismos(
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
    magnitud_minima: float = 4.0,
    latitud_minima: float = -56.0,
    latitud_maxima: float = -17.0,
    longitud_minima: float = -80.0,
    longitud_maxima: float = -65.0,
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
    if magnitud_minima < 0:
        raise ValueError("magnitud_minima debe ser mayor o igual a 0.")
    _validar_rangos_geograficos(
        latitud_minima, latitud_maxima, longitud_minima, longitud_maxima
    )

    if fecha_inicio is None:
        fecha_inicio = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    if fecha_fin is None:
        fecha_fin = datetime.now().strftime("%Y-%m-%d")

    fecha_inicio_dt = _validar_formato_fecha(fecha_inicio, "fecha_inicio")
    fecha_fin_dt = _validar_formato_fecha(fecha_fin, "fecha_fin")
    if fecha_inicio_dt > fecha_fin_dt:
        raise ValueError("fecha_inicio no puede ser posterior a fecha_fin.")

    params = {
        "format": "geojson",
        "starttime": fecha_inicio,
        "endtime": fecha_fin,
        "minlatitude": latitud_minima,
        "maxlatitude": latitud_maxima,
        "minlongitude": longitud_minima,
        "maxlongitude": longitud_maxima,
        "minmagnitude": magnitud_minima,
    }

    try:
        response = requests.get(USGS_URL, params=params, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise requests.RequestException(f"Error consultando API USGS: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise ValueError("La respuesta de USGS no es JSON válido.") from exc

    lista_sismos = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coords = geometry.get("coordinates", [None, None, None])

        lista_sismos.append(
            {
                "lugar": props.get("place"),
                "magnitud": props.get("mag"),
                "fecha": pd.to_datetime(props.get("time"), unit="ms", errors="coerce"),
                "longitud": coords[0] if len(coords) > 0 else None,
                "latitud": coords[1] if len(coords) > 1 else None,
                "profundidad": coords[2] if len(coords) > 2 else None,
            }
        )

    return pd.DataFrame(lista_sismos, columns=COLUMNAS_REQUERIDAS)


def limpiar_datos_sismos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y prepara los datos sísmicos para el análisis.

    Args:
        df: DataFrame con los datos sísmicos crudos.

    Returns:
        DataFrame con los datos limpios y procesados.
    """
    columnas_faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]
    if columnas_faltantes:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(columnas_faltantes)}")

    df_limpio = df[COLUMNAS_REQUERIDAS].copy()
    df_limpio["lugar"] = df_limpio["lugar"].fillna("Ubicación no informada")
    df_limpio["fecha"] = pd.to_datetime(df_limpio["fecha"], errors="coerce")

    for columna in ("magnitud", "latitud", "longitud", "profundidad"):
        df_limpio[columna] = pd.to_numeric(df_limpio[columna], errors="coerce")

    df_limpio = df_limpio.dropna(
        subset=["magnitud", "fecha", "latitud", "longitud", "profundidad"]
    )
    df_limpio = df_limpio[(df_limpio["magnitud"] > 0) & (df_limpio["profundidad"] >= 0)]

    return df_limpio.sort_values("fecha").reset_index(drop=True)


if __name__ == "__main__":
    df = obtener_datos_sismos()
    print(f"Se obtuvieron {len(df)} registros.")
    print(df.head())

    df_limpio = limpiar_datos_sismos(df)
    print(f"\nDespués de limpieza: {len(df_limpio)} registros.")
