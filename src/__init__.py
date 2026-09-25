"""
__init__.py - Paquete src del proyecto de Análisis Sísmico

Este paquete contiene los módulos principales para:
- Extracción y limpieza de datos sísmicos
- Visualización de datos
- Análisis estadístico y machine learning
"""

from .extraccion_datos import obtener_datos_sismos, limpiar_datos_sismos, guardar_dataset_analitico
from .visualizacion import (
    graficar_distribucion_magnitud,
    graficar_profundidad_vs_magnitud,
    graficar_distribucion_geografica,
    graficar_tasa_semanal,
    generar_todas_visualizaciones
)
from .analisis import (
    estadistica_descriptiva,
    analizar_relacion_magnitud_profundidad,
    agrupar_sismos,
    analizar_caracteristicas_grupos,
    generar_resumen_kpi,
    calcular_ley_gutenberg_richter,
    calcular_tasa_semanal
)

__version__ = '1.0.0'
__author__ = 'Jonathan Huenuanca'
