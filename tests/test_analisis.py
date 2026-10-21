"""Tests para extracción y análisis sísmico."""

from datetime import datetime
from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest
import requests

from src.analisis import (
    agrupar_sismos,
    analizar_caracteristicas_grupos,
    analizar_relacion_magnitud_profundidad,
    estadistica_descriptiva,
    generar_resumen_kpi,
)
from src.extraccion_datos import limpiar_datos_sismos, obtener_datos_sismos


@pytest.fixture
def dataframe_ejemplo() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "lugar": ["Santiago", "Valparaíso", "Concepción", "La Serena", "Antofagasta"],
            "magnitud": [4.5, 5.2, 6.1, 4.8, 5.5],
            "fecha": pd.date_range("2025-01-01", periods=5),
            "longitud": [-70.6, -71.6, -73.0, -71.2, -70.4],
            "latitud": [-33.4, -33.0, -36.8, -29.9, -23.6],
            "profundidad": [50.0, 80.0, 120.0, 45.0, 200.0],
        }
    )


class TestExtraccionDatos:
    def test_obtener_datos_sismos_ok_con_mock(self, monkeypatch):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "features": [
                {
                    "properties": {"place": "Chile", "mag": 5.2, "time": 1735689600000},
                    "geometry": {"coordinates": [-70.6, -33.4, 55.0]},
                }
            ]
        }
        mock_get = Mock(return_value=response)
        monkeypatch.setattr("src.extraccion_datos.requests.get", mock_get)

        df = obtener_datos_sismos(fecha_inicio="2025-01-01", fecha_fin="2025-01-31")

        assert len(df) == 1
        assert list(df.columns) == [
            "lugar",
            "magnitud",
            "fecha",
            "longitud",
            "latitud",
            "profundidad",
        ]
        mock_get.assert_called_once()
        _, kwargs = mock_get.call_args
        assert kwargs["timeout"] == 30

    def test_obtener_datos_sismos_fecha_invalida(self):
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            obtener_datos_sismos(fecha_inicio="2025/01/01")

    def test_obtener_datos_sismos_rango_fecha_invalido(self):
        with pytest.raises(ValueError, match="posterior"):
            obtener_datos_sismos(fecha_inicio="2025-02-01", fecha_fin="2025-01-01")

    def test_obtener_datos_sismos_http_error(self, monkeypatch):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError("boom")
        monkeypatch.setattr("src.extraccion_datos.requests.get", Mock(return_value=response))

        with pytest.raises(requests.RequestException):
            obtener_datos_sismos(fecha_inicio="2025-01-01", fecha_fin="2025-01-02")

    def test_obtener_datos_sismos_json_invalido(self, monkeypatch):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.side_effect = ValueError("json")
        monkeypatch.setattr("src.extraccion_datos.requests.get", Mock(return_value=response))

        with pytest.raises(ValueError, match="JSON"):
            obtener_datos_sismos(fecha_inicio="2025-01-01", fecha_fin="2025-01-02")

    def test_limpiar_datos_elimina_nulos_y_valores_invalidos(self):
        df = pd.DataFrame(
            {
                "lugar": ["A", None, "C", "D"],
                "magnitud": [4.5, None, -1, 5.0],
                "fecha": ["2025-01-01", "2025-01-02", "bad-date", "2025-01-04"],
                "longitud": [-70.0, -71.0, -72.0, -73.0],
                "latitud": [-33.0, -34.0, -35.0, -36.0],
                "profundidad": [50.0, 60.0, 70.0, 10.0],
            }
        )

        limpio = limpiar_datos_sismos(df)
        assert len(limpio) == 2
        assert limpio["magnitud"].min() > 0
        assert limpio["profundidad"].min() >= 0

    def test_limpiar_datos_falla_sin_columnas(self):
        with pytest.raises(ValueError, match="Faltan columnas"):
            limpiar_datos_sismos(pd.DataFrame({"magnitud": [4.5]}))


class TestAnalisis:
    def test_estadistica_descriptiva_retorna_dataframe(self, dataframe_ejemplo):
        stats = estadistica_descriptiva(dataframe_ejemplo)
        assert isinstance(stats, pd.DataFrame)
        assert "magnitud" in stats.columns

    def test_relacion_magnitud_profundidad_retorna_dict(self, dataframe_ejemplo):
        resultado = analizar_relacion_magnitud_profundidad(dataframe_ejemplo)
        assert isinstance(resultado, dict)
        assert "correlacion" in resultado
        assert "r2" in resultado

    def test_relacion_magnitud_profundidad_con_datos_vacios(self):
        df = pd.DataFrame(columns=["magnitud", "profundidad"])
        resultado = analizar_relacion_magnitud_profundidad(df)
        assert np.isnan(resultado["r2"])

    def test_agrupar_sismos_retorna_forma_correcta(self, dataframe_ejemplo):
        etiquetas, _ = agrupar_sismos(dataframe_ejemplo, n_grupos=2)
        assert len(etiquetas) == len(dataframe_ejemplo)
        assert len(np.unique(etiquetas[etiquetas >= 0])) == 2

    def test_agrupar_sismos_valida_parametros(self, dataframe_ejemplo):
        with pytest.raises(ValueError, match="mayor o igual a 2"):
            agrupar_sismos(dataframe_ejemplo, n_grupos=1)

    def test_agrupar_sismos_maneja_outliers(self, dataframe_ejemplo):
        df = dataframe_ejemplo.copy()
        df.loc[len(df)] = ["Outlier", 8.5, datetime(2025, 1, 15), -71.0, -30.0, 600.0]
        etiquetas, _ = agrupar_sismos(df, n_grupos=3)
        assert len(etiquetas) == len(df)

    def test_analizar_caracteristicas_grupos_retorna_dataframe(self, dataframe_ejemplo):
        etiquetas, _ = agrupar_sismos(dataframe_ejemplo, n_grupos=2)
        cluster_stats = analizar_caracteristicas_grupos(dataframe_ejemplo, etiquetas)
        assert isinstance(cluster_stats, pd.DataFrame)
        assert len(cluster_stats) == 2

    def test_generar_resumen_kpi_retorna_dict_con_claves(self, dataframe_ejemplo):
        kpis = generar_resumen_kpi(dataframe_ejemplo)
        assert isinstance(kpis, dict)
        assert kpis["total_sismos"] == 5
        assert "region_mas_activa" in kpis

    def test_generar_resumen_kpi_con_datos_vacios(self):
        df = pd.DataFrame(columns=["magnitud", "profundidad", "latitud", "longitud", "lugar"])
        kpis = generar_resumen_kpi(df)
        assert kpis["total_sismos"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
