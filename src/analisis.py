"""
Módulo de análisis estadístico y machine learning para datos sísmicos.

Este módulo proporciona funciones para realizar análisis estadísticos descriptivos
y modelos básicos de machine learning aplicados a datos sísmicos.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from typing import Tuple, Dict, Any


def estadistica_descriptiva(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula estadísticas descriptivas completas para los datos sísmicos.
    
    Args:
        df: DataFrame con los datos sísmicos.
    
    Returns:
        DataFrame con las estadísticas descriptivas.
    """
    stats = df.describe()
    
    additional_stats = pd.DataFrame({
        'magnitud': {
            'median': df['magnitud'].median(),
            'skewness': df['magnitud'].skew(),
            'kurtosis': df['magnitud'].kurtosis()
        },
        'profundidad': {
            'median': df['profundidad'].median(),
            'skewness': df['profundidad'].skew(),
            'kurtosis': df['profundidad'].kurtosis()
        }
    })
    
    stats = pd.concat([stats, additional_stats])
    
    return stats


def analizar_relacion_magnitud_profundidad(df: pd.DataFrame) -> Dict[str, float]:
    """
    Analiza la relación entre magnitud y profundidad usando correlación y regresión.
    
    Args:
        df: DataFrame con los datos sísmicos.
    
    Returns:
        Diccionario con los resultados del análisis.
    """
    correlation = df['magnitud'].corr(df['profundidad'])
    
    X = df[['profundidad']]
    y = df['magnitud']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    return {
        'correlacion': correlation,
        'pendiente': model.coef_[0],
        'intercepto': model.intercept_,
        'mse': mse,
        'r2': r2
    }


def agrupar_sismos(
    df: pd.DataFrame,
    n_grupos: int = 3,
    estandarizar: bool = True
) -> Tuple[np.ndarray, KMeans]:
    """
    Realiza clustering de sismos basado en magnitud y profundidad.
    
    Args:
        df: DataFrame con los datos sísmicos.
        n_grupos: Número de grupos/clusters a identificar.
        estandarizar: Si True, aplica estandarización z-score previa al clustering.
    
    Returns:
        Tupla con (etiquetas de grupo, modelo KMeans entrenado).
    """
    features = df[['magnitud', 'profundidad']].values
    
    scaler = None
    if estandarizar:
        scaler = StandardScaler()
        features = scaler.fit_transform(features)
    
    kmeans = KMeans(n_clusters=n_grupos, random_state=42, n_init=10)
    labels = kmeans.fit_predict(features)
    kmeans.scaler_ = scaler
    
    return labels, kmeans


def analizar_caracteristicas_grupos(df: pd.DataFrame, etiquetas: np.ndarray) -> pd.DataFrame:
    """
    Analiza las características de cada grupo identificado.
    
    Args:
        df: DataFrame con los datos sísmicos.
        etiquetas: Etiquetas de grupo para cada sismo.
    
    Returns:
        DataFrame con las características promedio de cada grupo.
    """
    df_with_clusters = df.copy()
    df_with_clusters['grupo'] = etiquetas
    
    cluster_stats = df_with_clusters.groupby('grupo').agg({
        'magnitud': ['mean', 'std', 'count'],
        'profundidad': ['mean', 'std'],
        'latitud': ['mean'],
        'longitud': ['mean']
    }).round(2)
    
    return cluster_stats


def generar_resumen_kpi(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Genera un resumen de KPIs (Key Performance Indicators) para el dashboard ejecutivo.
    
    Args:
        df: DataFrame con los datos sísmicos.
    
    Returns:
        Diccionario con los KPIs principales.
    """
    total_sismos = len(df)
    magnitud_promedio = df['magnitud'].mean()
    magnitud_maxima = df['magnitud'].max()
    profundidad_promedio = df['profundidad'].mean()
    profundidad_maxima = df['profundidad'].max()
    
    alta_magnitud_count = len(df[df['magnitud'] >= 6.0])
    moderada_magnitud_count = len(df[(df['magnitud'] >= 5.0) & (df['magnitud'] < 6.0)])
    baja_magnitud_count = len(df[(df['magnitud'] >= 4.0) & (df['magnitud'] < 5.0)])
    
    superficiales_count = len(df[df['profundidad'] < 70])
    intermedios_count = len(df[(df['profundidad'] >= 70) & (df['profundidad'] < 300)])
    profundos_count = len(df[df['profundidad'] >= 300])
    
    region_mas_activa = df.groupby('lugar').size().idxmax()
    eventos_region_activa = df.groupby('lugar').size().max()
    
    return {
        'total_sismos': total_sismos,
        'magnitud_promedio': round(magnitud_promedio, 2),
        'magnitud_maxima': magnitud_maxima,
        'profundidad_promedio_km': round(profundidad_promedio, 2),
        'profundidad_maxima_km': profundidad_maxima,
        'alta_magnitud_6_plus': alta_magnitud_count,
        'moderada_magnitud_5_6': moderada_magnitud_count,
        'baja_magnitud_4_5': baja_magnitud_count,
        'sismos_superficiales_70km': superficiales_count,
        'sismos_intermedios_70_300km': intermedios_count,
        'sismos_profundos_300km_plus': profundos_count,
        'region_mas_activa': region_mas_activa,
        'eventos_region_activa': eventos_region_activa
    }


def calcular_ley_gutenberg_richter(
    df: pd.DataFrame,
    intervalo_magnitud: float = 0.1
) -> Dict[str, float]:
    """
    Calcula parámetros de la ley Gutenberg-Richter: log10(N) = a - bM.
    
    Args:
        df: DataFrame con datos sísmicos.
        intervalo_magnitud: Tamaño de bin de magnitud para construir N acumulado.
    
    Returns:
        Diccionario con parámetros a, b y ajuste r2.
    """
    magnitudes = df['magnitud'].dropna().values
    if len(magnitudes) < 2:
        return {'a': np.nan, 'b': np.nan, 'r2': np.nan, 'n_bins': 0}
    
    min_mag = np.floor(magnitudes.min() / intervalo_magnitud) * intervalo_magnitud
    max_mag = np.ceil(magnitudes.max() / intervalo_magnitud) * intervalo_magnitud
    bins = np.arange(min_mag, max_mag + intervalo_magnitud, intervalo_magnitud)
    
    conteos, bordes = np.histogram(magnitudes, bins=bins)
    conteos_acumulados = np.cumsum(conteos[::-1])[::-1]
    centros = bordes[:-1] + (intervalo_magnitud / 2)
    
    validos = conteos_acumulados > 0
    x = centros[validos]
    y = np.log10(conteos_acumulados[validos])
    
    if len(x) < 2:
        return {'a': np.nan, 'b': np.nan, 'r2': np.nan, 'n_bins': int(len(x))}
    
    pendiente, intercepto = np.polyfit(x, y, 1)
    y_pred = pendiente * x + intercepto
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else np.nan
    
    return {
        'a': float(intercepto),
        'b': float(-pendiente),
        'r2': float(r2),
        'n_bins': int(len(x))
    }


def calcular_tasa_semanal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la tasa semanal de ocurrencia de sismos.
    
    Args:
        df: DataFrame con datos sísmicos.
    
    Returns:
        DataFrame con columnas de fecha semanal y eventos.
    """
    df_tiempo = df.copy()
    df_tiempo['fecha'] = pd.to_datetime(df_tiempo['fecha'])
    
    serie_semanal = (
        df_tiempo.set_index('fecha')
        .resample('W')
        .size()
    )
    
    tasa_semanal = serie_semanal.rename('eventos').reset_index()
    tasa_semanal['tasa_semanal'] = tasa_semanal['eventos']
    
    return tasa_semanal


if __name__ == "__main__":
    from src.extraccion_datos import obtener_datos_sismos, limpiar_datos_sismos
    
    df = obtener_datos_sismos()
    df = limpiar_datos_sismos(df)
    
    print("=" * 60)
    print("ESTADÍSTICAS DESCRIPTIVAS")
    print("=" * 60)
    stats = estadistica_descriptiva(df)
    print(stats)
    
    print("\n" + "=" * 60)
    print("ANÁLISIS MAGNITUD-PROFUNDIDAD")
    print("=" * 60)
    relationship = analizar_relacion_magnitud_profundidad(df)
    for key, value in relationship.items():
        print(f"{key}: {value:.4f}")
    
    print("\n" + "=" * 60)
    print("CLUSTERING")
    print("=" * 60)
    labels, model = agrupar_sismos(df, n_grupos=3)
    cluster_stats = analizar_caracteristicas_grupos(df, labels)
    print(cluster_stats)
    
    print("\n" + "=" * 60)
    print("KPIs EJECUTIVOS")
    print("=" * 60)
    kpis = generar_resumen_kpi(df)
    for key, value in kpis.items():
        print(f"{key}: {value}")
