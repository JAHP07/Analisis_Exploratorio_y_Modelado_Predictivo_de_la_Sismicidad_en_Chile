"""
__init__.py - Paquete src del proyecto de Análisis Sísmico

Este paquete contiene los módulos principales para:
- Extracción y limpieza de datos sísmicos
- Visualización de datos
- Análisis estadístico y machine learning
"""

from .analisis import (
    agrupar_sismos,
    analizar_caracteristicas_grupos,
    analizar_relacion_magnitud_profundidad,
    estadistica_descriptiva,
    generar_resumen_kpi,
)
from .extraccion_datos import limpiar_datos_sismos, obtener_datos_sismos
from .visualizacion import (
    generar_todas_visualizaciones,
    graficar_distribucion_geografica,
    graficar_distribucion_magnitud,
    graficar_profundidad_vs_magnitud,
)

__all__ = [
    "obtener_datos_sismos",
    "limpiar_datos_sismos",
    "graficar_distribucion_magnitud",
    "graficar_profundidad_vs_magnitud",
    "graficar_distribucion_geografica",
    "generar_todas_visualizaciones",
    "estadistica_descriptiva",
    "analizar_relacion_magnitud_profundidad",
    "agrupar_sismos",
    "analizar_caracteristicas_grupos",
    "generar_resumen_kpi",
]

__version__ = "1.0.0"
__author__ = "Jonathan Huenuanca"
