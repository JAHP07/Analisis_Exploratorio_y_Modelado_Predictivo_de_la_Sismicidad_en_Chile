"""Tests para el módulo de visualización."""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import pytest

from src.visualizacion import (
    generar_todas_visualizaciones,
    graficar_distribucion_geografica,
    graficar_distribucion_magnitud,
    graficar_profundidad_vs_magnitud,
)


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


class TestVisualizacion:
    def test_graficar_distribucion_magnitud_retorna_figura(self, dataframe_ejemplo):
        fig = graficar_distribucion_magnitud(dataframe_ejemplo)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_graficar_profundidad_vs_magnitud_retorna_figura(self, dataframe_ejemplo):
        fig = graficar_profundidad_vs_magnitud(dataframe_ejemplo)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_graficar_distribucion_geografica_retorna_figura(self, dataframe_ejemplo):
        fig = graficar_distribucion_geografica(dataframe_ejemplo)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_generar_todas_visualizaciones_crea_archivos(self, dataframe_ejemplo, tmp_path):
        output_dir = str(tmp_path / "output")
        paths = generar_todas_visualizaciones(dataframe_ejemplo, output_dir=output_dir)

        assert len(paths) == 3
        for path in paths.values():
            assert os.path.exists(path)

    def test_visualizacion_falla_con_datos_vacios(self):
        df = pd.DataFrame(columns=["magnitud", "profundidad", "latitud", "longitud"])
        with pytest.raises(ValueError, match="No hay datos suficientes"):
            graficar_distribucion_magnitud(df)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
