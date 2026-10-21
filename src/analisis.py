"""Módulo de análisis estadístico y machine learning para datos sísmicos."""

from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

COLUMNAS_BASE = ["magnitud", "profundidad", "latitud", "longitud", "lugar"]


def _validar_columnas(df: pd.DataFrame, columnas: list[str]) -> None:
    faltantes = [c for c in columnas if c not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas para análisis: {', '.join(faltantes)}")


def estadistica_descriptiva(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula estadísticas descriptivas para datos sísmicos."""
    _validar_columnas(df, ["magnitud", "profundidad"])
    if df.empty:
        return pd.DataFrame()

    base = df[["magnitud", "profundidad"]].describe()
    adicionales = pd.DataFrame(
        {
            "magnitud": {
                "median": df["magnitud"].median(),
                "skewness": df["magnitud"].skew(),
                "kurtosis": df["magnitud"].kurtosis(),
            },
            "profundidad": {
                "median": df["profundidad"].median(),
                "skewness": df["profundidad"].skew(),
                "kurtosis": df["profundidad"].kurtosis(),
            },
        }
    )
    return pd.concat([base, adicionales])


def analizar_relacion_magnitud_profundidad(df: pd.DataFrame) -> dict[str, float]:
    """Analiza relación magnitud-profundidad con correlación y regresión lineal."""
    _validar_columnas(df, ["magnitud", "profundidad"])

    datos = df[["magnitud", "profundidad"]].dropna().copy()
    if len(datos) < 3:
        return {
            "correlacion": np.nan,
            "pendiente": np.nan,
            "intercepto": np.nan,
            "mse": np.nan,
            "r2": np.nan,
            "n_muestras": float(len(datos)),
        }

    correlation = datos["magnitud"].corr(datos["profundidad"])
    x = datos[["profundidad"]]
    y = datos["magnitud"]

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = (
        r2_score(y_test, y_pred)
        if len(y_test) >= 2
        else float("nan")
        if len(y_test) >= 2
        else float("nan")
        if len(y_test) >= 2
        else float("nan")
    )

    return {
        "correlacion": float(correlation),
        "pendiente": float(model.coef_[0]),
        "intercepto": float(model.intercept_),
        "mse": float(mse),
        "r2": float(r2),
        "n_muestras": float(len(datos)),
    }


def agrupar_sismos(df: pd.DataFrame, n_grupos: int = 3) -> tuple[np.ndarray, KMeans]:
    """Realiza clustering de sismos con K-Means usando magnitud y profundidad."""
    _validar_columnas(df, ["magnitud", "profundidad"])

    if n_grupos < 2:
        raise ValueError("n_grupos debe ser mayor o igual a 2.")

    datos = df[["magnitud", "profundidad"]].dropna().copy()
    if len(datos) < n_grupos:
        raise ValueError("No hay suficientes registros para el número de grupos solicitado.")

    features = datos.values
    kmeans = KMeans(n_clusters=n_grupos, random_state=42, n_init=10)
    labels = kmeans.fit_predict(features)

    etiquetas = np.full(len(df), -1)
    # Preserve row positions independently of the original DataFrame index.
    posiciones_validas = np.flatnonzero(
        df[["magnitud", "profundidad"]].notna().all(axis=1).to_numpy()
    )
    etiquetas[posiciones_validas] = labels
    return etiquetas, kmeans


def analizar_caracteristicas_grupos(df: pd.DataFrame, etiquetas: np.ndarray) -> pd.DataFrame:
    """Calcula estadísticas por grupo del clustering."""
    _validar_columnas(df, ["magnitud", "profundidad", "latitud", "longitud"])
    if len(df) != len(etiquetas):
        raise ValueError("La cantidad de etiquetas debe coincidir con la cantidad de registros.")

    df_with_clusters = df.copy()
    df_with_clusters["grupo"] = etiquetas
    df_with_clusters = df_with_clusters[df_with_clusters["grupo"] >= 0]

    if df_with_clusters.empty:
        return pd.DataFrame()

    return (
        df_with_clusters.groupby("grupo")
        .agg(
            {
                "magnitud": ["mean", "std", "count"],
                "profundidad": ["mean", "std"],
                "latitud": ["mean"],
                "longitud": ["mean"],
            }
        )
        .round(2)
    )


def generar_resumen_kpi(df: pd.DataFrame) -> dict[str, Any]:
    """Genera KPIs ejecutivos del dataset sísmico."""
    _validar_columnas(df, COLUMNAS_BASE)

    if df.empty:
        return {
            "total_sismos": 0,
            "magnitud_promedio": np.nan,
            "magnitud_maxima": np.nan,
            "profundidad_promedio_km": np.nan,
            "profundidad_maxima_km": np.nan,
            "alta_magnitud_6_plus": 0,
            "moderada_magnitud_5_6": 0,
            "baja_magnitud_4_5": 0,
            "sismos_superficiales_70km": 0,
            "sismos_intermedios_70_300km": 0,
            "sismos_profundos_300km_plus": 0,
            "region_mas_activa": None,
            "eventos_region_activa": 0,
        }

    total_sismos = len(df)
    magnitud_promedio = df["magnitud"].mean()
    magnitud_maxima = df["magnitud"].max()
    profundidad_promedio = df["profundidad"].mean()
    profundidad_maxima = df["profundidad"].max()

    alta_magnitud_count = len(df[df["magnitud"] >= 6.0])
    moderada_magnitud_count = len(df[(df["magnitud"] >= 5.0) & (df["magnitud"] < 6.0)])
    baja_magnitud_count = len(df[(df["magnitud"] >= 4.0) & (df["magnitud"] < 5.0)])

    superficiales_count = len(df[df["profundidad"] < 70])
    intermedios_count = len(df[(df["profundidad"] >= 70) & (df["profundidad"] < 300)])
    profundos_count = len(df[df["profundidad"] >= 300])

    region_counts = df["lugar"].fillna("Ubicación no informada").value_counts()
    region_mas_activa = region_counts.index[0] if not region_counts.empty else None
    eventos_region_activa = int(region_counts.iloc[0]) if not region_counts.empty else 0

    return {
        "total_sismos": int(total_sismos),
        "magnitud_promedio": round(float(magnitud_promedio), 2),
        "magnitud_maxima": float(magnitud_maxima),
        "profundidad_promedio_km": round(float(profundidad_promedio), 2),
        "profundidad_maxima_km": float(profundidad_maxima),
        "alta_magnitud_6_plus": int(alta_magnitud_count),
        "moderada_magnitud_5_6": int(moderada_magnitud_count),
        "baja_magnitud_4_5": int(baja_magnitud_count),
        "sismos_superficiales_70km": int(superficiales_count),
        "sismos_intermedios_70_300km": int(intermedios_count),
        "sismos_profundos_300km_plus": int(profundos_count),
        "region_mas_activa": region_mas_activa,
        "eventos_region_activa": eventos_region_activa,
    }


if __name__ == "__main__":
    from src.extraccion_datos import limpiar_datos_sismos, obtener_datos_sismos

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
        print(f"{key}: {value}")

    print("\n" + "=" * 60)
    print("CLUSTERING")
    print("=" * 60)
    labels, _ = agrupar_sismos(df, n_grupos=3)
    cluster_stats = analizar_caracteristicas_grupos(df, labels)
    print(cluster_stats)

    print("\n" + "=" * 60)
    print("KPIs EJECUTIVOS")
    print("=" * 60)
    kpis = generar_resumen_kpi(df)
    for key, value in kpis.items():
        print(f"{key}: {value}")
