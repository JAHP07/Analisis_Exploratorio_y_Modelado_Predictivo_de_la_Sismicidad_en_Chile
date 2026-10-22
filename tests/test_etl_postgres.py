"""Pruebas offline del ETL PostgreSQL (sin credenciales ni servidor)."""

from datetime import UTC
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests

from src.etl_postgres import (
    ESQUEMA_SQL,
    UPSERT_SQL,
    aplicar_esquema,
    cargar_eventos,
    consultar_usgs,
    normalizar_eventos,
    validar_periodo,
)


def ejemplo():
    return {
        "features": [
            {
                "id": "us123456",
                "properties": {
                    "place": "42 km de Valparaíso",
                    "mag": 5.2,
                    "time": 1760000000000,
                    "updated": 1760000001000,
                },
                "geometry": {"coordinates": [-71.6, -33.0, 30.0]},
            }
        ],
        "metadata": {"count": 1},
    }


@pytest.mark.parametrize(
    "desde,hasta,magnitud",
    [
        ("2026/09/01", "2026-09-30", 4),
        ("2026-10-03", "2026-10-01", 4),
        ("2026-09-01", "2026-09-30", 0),
        ("2026-09-01", "2026-09-30", 11),
    ],
)
def test_valida_parametros(desde, hasta, magnitud):
    with pytest.raises(ValueError):
        validar_periodo(desde, hasta, magnitud)


def test_normaliza_id_oficial_fecha_utc_y_tipos():
    eventos, descartados = normalizar_eventos(ejemplo())
    assert descartados == 0
    assert eventos[0]["id_usgs"] == "us123456"
    assert eventos[0]["magnitud"] == 5.2
    assert eventos[0]["fecha"].tzinfo is UTC
    assert eventos[0]["actualizado_usgs_ms"] == 1760000001000


def test_descarta_registros_incompletos():
    data = ejemplo()
    data["features"].append({"id": "sin-coords", "properties": {"mag": 4}})
    eventos, descartados = normalizar_eventos(data)
    assert len(eventos) == 1
    assert descartados == 1


def test_descarta_nan():
    data = ejemplo()
    data["features"][0]["properties"]["mag"] = float("nan")
    eventos, descartados = normalizar_eventos(data)
    assert len(eventos) == 0
    assert descartados == 1


def test_geojson_invalido():
    with pytest.raises(ValueError):
        normalizar_eventos({"features": None})


def test_consultar_usgs_sin_red(monkeypatch):
    response = Mock()
    response.json.return_value = ejemplo()
    response.raise_for_status.return_value = None
    get = Mock(return_value=response)
    monkeypatch.setattr("src.etl_postgres.requests.get", get)
    result = consultar_usgs("2026-09-01", "2026-09-30")
    assert result["features"][0]["id"] == "us123456"
    assert get.call_args.kwargs["timeout"] == 30
    assert get.call_args.kwargs["params"]["minmagnitude"] == 4.0


def test_consulta_propagacion_http(monkeypatch):
    def fallo(*_args, **_kwargs):
        raise requests.Timeout("tiempo agotado")

    monkeypatch.setattr("src.etl_postgres.requests.get", fallo)
    with pytest.raises(requests.Timeout):
        consultar_usgs("2026-09-01", "2026-09-30")


def test_consulta_no_trunca_silenciosamente(monkeypatch):
    response = Mock()
    data = ejemplo()
    data["metadata"]["count"] = 20000
    response.json.return_value = data
    monkeypatch.setattr("src.etl_postgres.requests.get", Mock(return_value=response))
    with pytest.raises(ValueError, match="límite USGS"):
        consultar_usgs("2026-09-01", "2026-09-30")


class CursorFalso:
    def __init__(self):
        self.executed = []
        self.batch = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, consulta):
        self.executed.append(consulta)

    def executemany(self, consulta, filas):
        self.batch.append((consulta, filas))


class ConexionFalsa:
    def __init__(self):
        self.cursor_falso = CursorFalso()

    def cursor(self):
        return self.cursor_falso


def test_esquema_y_upsert_idempotente_por_id():
    conexion = ConexionFalsa()
    aplicar_esquema(conexion)
    assert "CREATE TABLE IF NOT EXISTS eventos_sismicos" in conexion.cursor_falso.executed[0]
    assert "id_usgs TEXT PRIMARY KEY" in Path(ESQUEMA_SQL).read_text(encoding="utf-8")
    eventos, _ = normalizar_eventos(ejemplo())
    assert cargar_eventos(conexion, eventos) == 1
    assert len(conexion.cursor_falso.batch[0][1]) == 1
    assert "ON CONFLICT (id_usgs)" in UPSERT_SQL
    assert "EXCLUDED.actualizado_usgs_ms >" in UPSERT_SQL


def test_cargar_vacio_no_abre_cursor():
    conexion = ConexionFalsa()
    assert cargar_eventos(conexion, []) == 0
    assert conexion.cursor_falso.batch == []
