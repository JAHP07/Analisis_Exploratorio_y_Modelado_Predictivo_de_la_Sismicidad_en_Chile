"""
Tests para el módulo de visualización.
"""

import pytest
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo para testing
import matplotlib.pyplot as plt
from src.visualizacion import (
    graficar_distribucion_magnitud,
    graficar_profundidad_vs_magnitud,
    graficar_distribucion_geografica,
    graficar_tasa_semanal,
    generar_todas_visualizaciones
)
from src.analisis import calcular_tasa_semanal


@pytest.fixture
def dataframe_ejemplo():
    """Crea un DataFrame de ejemplo para testing."""
    data = {
        'lugar': ['Santiago', 'Valparaíso', 'Concepción', 'La Serena', 'Antofagasta'],
        'magnitud': [4.5, 5.2, 6.1, 4.8, 5.5],
        'fecha': pd.date_range('2025-01-01', periods=5),
        'longitud': [-70.6, -71.6, -73.0, -71.2, -70.4],
        'latitud': [-33.4, -33.0, -36.8, -29.9, -23.6],
        'profundidad': [50.0, 80.0, 120.0, 45.0, 200.0]
    }
    return pd.DataFrame(data)


class TestVisualizacion:
    """Tests para el módulo de visualización."""
    
    def test_graficar_distribucion_magnitud_retorna_figura(self, dataframe_ejemplo):
        """Verifica que el gráfico de magnitudes retorne una figura."""
        fig = graficar_distribucion_magnitud(dataframe_ejemplo)
        assert fig is not None
        assert isinstance(fig, plt.Figure)
        plt.close(fig)
    
    def test_graficar_profundidad_vs_magnitud_retorna_figura(self, dataframe_ejemplo):
        """Verifica que el gráfico profundidad vs magnitud retorne una figura."""
        fig = graficar_profundidad_vs_magnitud(dataframe_ejemplo)
        assert fig is not None
        assert isinstance(fig, plt.Figure)
        plt.close(fig)
    
    def test_graficar_distribucion_geografica_retorna_figura(self, dataframe_ejemplo):
        """Verifica que el gráfico geográfico retorne una figura."""
        fig = graficar_distribucion_geografica(dataframe_ejemplo)
        assert fig is not None
        assert isinstance(fig, plt.Figure)
        plt.close(fig)
    
    def test_generar_todas_visualizaciones_crea_archivos(self, dataframe_ejemplo, tmp_path):
        """Verifica que se generen todos los archivos de visualización."""
        output_dir = str(tmp_path / "output")
        paths = generar_todas_visualizaciones(dataframe_ejemplo, output_dir=output_dir)
        
        assert len(paths) == 4
        assert 'distribucion_magnitud' in paths
        assert 'profundidad_vs_magnitud' in paths
        assert 'distribucion_geografica' in paths
        assert 'tasa_semanal' in paths
    
    def test_graficar_tasa_semanal_retorna_figura(self, dataframe_ejemplo):
        """Verifica que el gráfico de tasa semanal retorne una figura."""
        df_tasa = calcular_tasa_semanal(dataframe_ejemplo)
        fig = graficar_tasa_semanal(df_tasa)
        assert fig is not None
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
