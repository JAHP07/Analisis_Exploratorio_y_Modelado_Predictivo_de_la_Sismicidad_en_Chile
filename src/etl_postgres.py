"""ETL incremental de eventos sísmicos USGS hacia PostgreSQL.

El código original de extracción y sus funciones públicas no se modifican.
"""

from __future__ import annotations

from datetime import UTC, datetime
from math import isfinite
from pathlib import Path

import requests

from src.extraccion_datos import USGS_URL

ESQUEMA_SQL = Path(__file__).resolve().parents[1] / "sql" / "001_eventos_sismicos.sql"
LIMITE_USGS = 20000

UPSERT_SQL = """
INSERT INTO eventos_sismicos (
    id_usgs, fecha, magnitud, profundidad_km, latitud, longitud,
    lugar, actualizado_usgs_ms
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (id_usgs) DO UPDATE SET
    fecha = EXCLUDED.fecha,
    magnitud = EXCLUDED.magnitud,
    profundidad_km = EXCLUDED.profundidad_km,
    latitud = EXCLUDED.latitud,
    longitud = EXCLUDED.longitud,
    lugar = EXCLUDED.lugar,
    actualizado_usgs_ms = EXCLUDED.actualizado_usgs_ms,
    fecha_ingesta = CURRENT_TIMESTAMP
WHERE EXCLUDED.actualizado_usgs_ms > eventos_sismicos.actualizado_usgs_ms;
"""


def validar_periodo(desde: str, hasta: str, magnitud_minima: float = 4.0) -> None:
    """Requiere fechas ISO ordenadas y una magnitud positiva."""
    try:
        inicio = datetime.strptime(desde, "%Y-%m-%d")
        fin = datetime.strptime(hasta, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Las fechas deben usar YYYY-MM-DD") from exc
    if inicio > fin:
        raise ValueError("--desde debe ser anterior o igual a --hasta")
    if not 0 < magnitud_minima <= 10:
        raise ValueError("--magnitud-minima debe estar entre 0 (exclusivo) y 10")


def consultar_usgs(desde: str, hasta: str, magnitud_minima: float = 4.0) -> dict:
    """Obtiene GeoJSON de USGS en el rectángulo geográfico de Chile."""
    validar_periodo(desde, hasta, magnitud_minima)
    parametros = {
        "format": "geojson",
        "starttime": desde,
        "endtime": hasta,
        "minmagnitude": magnitud_minima,
        "minlatitude": -56,
        "maxlatitude": -17,
        "minlongitude": -80,
        "maxlongitude": -65,
        "limit": LIMITE_USGS,
        "orderby": "time-asc",
    }
    respuesta = requests.get(USGS_URL, params=parametros, timeout=30)
    respuesta.raise_for_status()
    try:
        documento = respuesta.json()
    except ValueError as exc:
        raise ValueError("La API USGS devolvió JSON inválido") from exc
    if not isinstance(documento, dict) or not isinstance(documento.get("features"), list):
        raise ValueError("La API USGS no devolvió una lista válida de eventos")

    # Evita tratar como muestra completa una respuesta posiblemente truncada.
    metadata = documento.get("metadata")
    reportados = metadata.get("count", 0) if isinstance(metadata, dict) else 0
    if len(documento["features"]) >= LIMITE_USGS or (
        isinstance(reportados, int) and reportados >= LIMITE_USGS
    ):
        raise ValueError("La consulta alcanzó el límite USGS: usa períodos más cortos")
    return documento


def normalizar_eventos(documento: dict) -> tuple[list[dict], int]:
    """Transforma GeoJSON en eventos tipados. Descarta registros incompletos.

    Devuelve (eventos_validos, descartados). Mantiene la ID oficial de USGS.
    """
    if not isinstance(documento, dict) or not isinstance(documento.get("features"), list):
        raise ValueError("Se esperaba GeoJSON con 'features' en forma de lista")
    eventos = []
    descartados = 0
    for feature in documento["features"]:
        try:
            if not isinstance(feature, dict):
                raise ValueError("Evento inválido")
            id_usgs = feature["id"]
            propiedades = feature["properties"]
            coordenadas = feature["geometry"]["coordinates"]
            if not isinstance(id_usgs, str) or not id_usgs.strip():
                raise ValueError("Sin identificador USGS")
            if not isinstance(propiedades, dict) or not isinstance(coordenadas, list):
                raise ValueError("Geometría o propiedades inválidas")
            if len(coordenadas) < 3:
                raise ValueError("Coordenadas incompletas")
            longitud, latitud, profundidad = (float(coordenadas[i]) for i in range(3))
            magnitud = float(propiedades["mag"])
            fecha_ms = int(propiedades["time"])
            actualizado_ms = int(propiedades.get("updated") or 0)
            if not (
                0 < magnitud <= 10
                and -90 <= latitud <= 90
                and -180 <= longitud <= 180
                and profundidad >= 0
                and fecha_ms > 0
                and actualizado_ms >= 0
            ):
                raise ValueError("Evento fuera de límites válidos")
            # SQL rechaza no-finitos y estos valores carecen de significado analítico.
            if not all(isfinite(v) for v in (magnitud, profundidad, latitud, longitud)):
                raise ValueError("Coordenadas o magnitud no finitas")
            lugar = propiedades.get("place")
            eventos.append(
                {
                    "id_usgs": id_usgs,
                    "fecha": datetime.fromtimestamp(fecha_ms / 1000, UTC),
                    "magnitud": magnitud,
                    "profundidad_km": profundidad,
                    "latitud": latitud,
                    "longitud": longitud,
                    "lugar": lugar.strip()
                    if isinstance(lugar, str) and lugar.strip()
                    else "Desconocido",
                    "actualizado_usgs_ms": actualizado_ms,
                }
            )
        except (KeyError, TypeError, ValueError, IndexError, OverflowError, OSError):
            descartados += 1
    return eventos, descartados


def aplicar_esquema(conexion) -> None:
    """Inicializa tabla e índices (DDL idempotente)."""
    with conexion.cursor() as cursor:
        cursor.execute(ESQUEMA_SQL.read_text(encoding="utf-8"))


def cargar_eventos(conexion, eventos: list[dict]) -> int:
    """Hace UPSERT por USGS ID; retorna eventos enviados, no filas insertadas."""
    filas = [
        (
            e["id_usgs"],
            e["fecha"],
            e["magnitud"],
            e["profundidad_km"],
            e["latitud"],
            e["longitud"],
            e["lugar"],
            e["actualizado_usgs_ms"],
        )
        for e in eventos
    ]
    if filas:
        with conexion.cursor() as cursor:
            cursor.executemany(UPSERT_SQL, filas)
    return len(filas)
