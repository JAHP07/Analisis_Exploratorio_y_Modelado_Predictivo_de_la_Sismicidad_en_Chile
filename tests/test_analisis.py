"""
Tests para los módulos del proyecto de análisis sísmico.
"""

import os
import pytest
import pandas as pd
import numpy as np
from src.extraccion_datos import limpiar_datos_sismos, guardar_dataset_analitico
from src.analisis import (
    estadistica_descriptiva,
    analizar_relacion_magnitud_profundidad,
    agrupar_sismos,
    analizar_caracteristicas_grupos,
    generar_resumen_kpi,
    calcular_ley_gutenberg_richter,
    calcular_tasa_semanal
)


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


class TestExtraccionDatos:
    """Tests para el módulo de extracción de datos."""
    
    def test_limpiar_datos_no_elimina_completos(self, dataframe_ejemplo):
        """Verifica que no se eliminen datos cuando están completos."""
        limpio = limpiar_datos_sismos(dataframe_ejemplo)
        assert len(limpio) == len(dataframe_ejemplo)
    
    def test_limpiar_datos_manaja_valores_faltantes(self):
        """Verifica que se manejen valores faltantes correctamente."""
        data = {
            'lugar': ['A', 'B', 'C'],
            'magnitud': [4.5, None, 5.0],
            'fecha': pd.date_range('2025-01-01', periods=3),
            'longitud': [-70.0, -71.0, -72.0],
            'latitud': [-33.0, -34.0, -35.0],
            'profundidad': [50.0, 60.0, 70.0]
        }
        df = pd.DataFrame(data)
        limpio = limpiar_datos_sismos(df)
        assert len(limpio) == 2
    
    def test_limpiar_datos_filtra_magnitud_negativa(self):
        """Verifica que se filtren magnitudes negativas."""
        data = {
            'lugar': ['A', 'B', 'C'],
            'magnitud': [4.5, -1.0, 5.0],
            'fecha': pd.date_range('2025-01-01', periods=3),
            'longitud': [-70.0, -71.0, -72.0],
            'latitud': [-33.0, -34.0, -35.0],
            'profundidad': [50.0, 60.0, 70.0]
        }
        df = pd.DataFrame(data)
        limpio = limpiar_datos_sismos(df)
        assert len(limpio) == 2
    
    def test_guardar_dataset_analitico_columnas_esperadas(self, dataframe_ejemplo, tmp_path):
        """Verifica que el dataset analítico se guarde con columnas clave."""
        file_path = tmp_path / "dataset_analitico.csv"
        resultado = guardar_dataset_analitico(dataframe_ejemplo, str(file_path))
        
        assert os.path.exists(file_path)
        assert list(resultado.columns) == [
            'magnitud', 'fecha', 'hora', 'latitud', 'profundidad_km'
        ]


class TestAnalisis:
    """Tests para el módulo de análisis."""
    
    def test_estadistica_descriptiva_retorna_dataframe(self, dataframe_ejemplo):
        """Verifica que las estadísticas descriptivas retornen un DataFrame."""
        stats = estadistica_descriptiva(dataframe_ejemplo)
        assert isinstance(stats, pd.DataFrame)
        assert 'magnitud' in stats.columns or 'magnitud' in stats.index
    
    def test_relacion_magnitud_profundidad_retorna_dict(self, dataframe_ejemplo):
        """Verifica que el análisis de relación retorne un diccionario."""
        resultado = analizar_relacion_magnitud_profundidad(dataframe_ejemplo)
        assert isinstance(resultado, dict)
        assert 'correlacion' in resultado
        assert 'r2' in resultado
    
    def test_agrupar_sismos_retorna_forma_correcta(self, dataframe_ejemplo):
        """Verifica que el clustering retorne la forma correcta."""
        etiquetas, modelo = agrupar_sismos(dataframe_ejemplo, n_grupos=2)
        assert len(etiquetas) == len(dataframe_ejemplo)
        assert len(np.unique(etiquetas)) == 2
        assert hasattr(modelo, 'scaler_')
        assert modelo.scaler_ is not None
    
    def test_analizar_caracteristicas_grupos_retorna_dataframe(self, dataframe_ejemplo):
        """Verifica que el análisis de grupos retorne un DataFrame."""
        etiquetas, _ = agrupar_sismos(dataframe_ejemplo, n_grupos=2)
        cluster_stats = analizar_caracteristicas_grupos(dataframe_ejemplo, etiquetas)
        assert isinstance(cluster_stats, pd.DataFrame)
        assert len(cluster_stats) == 2
    
    def test_generar_resumen_kpi_retorna_dict_con_claves(self, dataframe_ejemplo):
        """Verifica que los KPIs tengan las llaves esperadas."""
        kpis = generar_resumen_kpi(dataframe_ejemplo)
        assert isinstance(kpis, dict)
        assert 'total_sismos' in kpis
        assert 'magnitud_promedio' in kpis
        assert 'magnitud_maxima' in kpis
        assert kpis['total_sismos'] == 5
    
    def test_calcular_ley_gutenberg_richter_retorna_parametros(self, dataframe_ejemplo):
        """Verifica salida esperada de ley Gutenberg-Richter."""
        resultado = calcular_ley_gutenberg_richter(dataframe_ejemplo)
        assert isinstance(resultado, dict)
        assert 'a' in resultado
        assert 'b' in resultado
        assert 'r2' in resultado
        assert 'n_bins' in resultado
    
    def test_calcular_tasa_semanal_retorna_dataframe(self, dataframe_ejemplo):
        """Verifica cálculo de tasa semanal."""
        tasa = calcular_tasa_semanal(dataframe_ejemplo)
        assert isinstance(tasa, pd.DataFrame)
        assert 'fecha' in tasa.columns
        assert 'eventos' in tasa.columns
        assert 'tasa_semanal' in tasa.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
