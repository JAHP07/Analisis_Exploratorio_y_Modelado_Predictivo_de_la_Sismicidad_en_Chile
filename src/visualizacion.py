"""Módulo de visualización de datos sísmicos."""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def _validar_datos_grafico(df: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    faltantes = [c for c in columnas if c not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas para graficar: {', '.join(faltantes)}")

    datos = df.dropna(subset=columnas)
    if datos.empty:
        raise ValueError("No hay datos suficientes para generar la visualización.")
    return datos


def _guardar_figura(save_path: str | None) -> None:
    if not save_path:
        return
    directory = os.path.dirname(save_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches="tight")


def graficar_distribucion_magnitud(
    df: pd.DataFrame,
    figsize: tuple[int, int] = (10, 5),
    save_path: str | None = None,
) -> plt.Figure:
    """Genera un histograma de la distribución de magnitudes."""
    datos = _validar_datos_grafico(df, ["magnitud"])

    fig, ax = plt.subplots(figsize=figsize)
    sns.histplot(data=datos, x="magnitud", bins=10, kde=True, color="crimson", ax=ax)
    ax.set_title("Distribución de Magnitudes de Sismos Recientes en Chile", fontsize=14)
    ax.set_xlabel("Magnitud")
    ax.set_ylabel("Frecuencia")

    _guardar_figura(save_path)
    return fig


def graficar_profundidad_vs_magnitud(
    df: pd.DataFrame,
    figsize: tuple[int, int] = (10, 5),
    save_path: str | None = None,
) -> plt.Figure:
    """Genera un scatter plot de profundidad vs magnitud."""
    datos = _validar_datos_grafico(df, ["magnitud", "profundidad"])

    fig, ax = plt.subplots(figsize=figsize)
    sns.scatterplot(
        data=datos,
        x="magnitud",
        y="profundidad",
        size="magnitud",
        sizes=(50, 200),
        alpha=0.7,
        ax=ax,
    )
    ax.invert_yaxis()
    ax.set_title("Profundidad vs Magnitud del Sismo", fontsize=14)
    ax.set_xlabel("Magnitud")
    ax.set_ylabel("Profundidad (km)")

    _guardar_figura(save_path)
    return fig


def graficar_distribucion_geografica(
    df: pd.DataFrame,
    figsize: tuple[int, int] = (6, 8),
    save_path: str | None = None,
) -> plt.Figure:
    """Genera un mapa de dispersión geográfica de los epicentros."""
    datos = _validar_datos_grafico(df, ["latitud", "longitud", "magnitud"])

    fig, ax = plt.subplots(figsize=figsize)
    sns.scatterplot(
        data=datos,
        x="longitud",
        y="latitud",
        hue="magnitud",
        size="magnitud",
        sizes=(40, 250),
        palette="flare",
        alpha=0.8,
        ax=ax,
    )
    ax.set_title("Distribución Geográfica de Sismos", fontsize=14)
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()

    _guardar_figura(save_path)
    return fig


def generar_todas_visualizaciones(df: pd.DataFrame, output_dir: str = "output") -> dict:
    """Genera todas las visualizaciones y devuelve sus rutas."""
    paths = {
        "distribucion_magnitud": os.path.join(output_dir, "distribucion_magnitud.png"),
        "profundidad_vs_magnitud": os.path.join(output_dir, "profundidad_vs_magnitud.png"),
        "distribucion_geografica": os.path.join(output_dir, "distribucion_geografica.png"),
    }

    graficar_distribucion_magnitud(df, save_path=paths["distribucion_magnitud"])
    graficar_profundidad_vs_magnitud(df, save_path=paths["profundidad_vs_magnitud"])
    graficar_distribucion_geografica(df, save_path=paths["distribucion_geografica"])
    return paths


if __name__ == "__main__":
    from src.extraccion_datos import limpiar_datos_sismos, obtener_datos_sismos

    df = obtener_datos_sismos()
    df = limpiar_datos_sismos(df)

    paths = generar_todas_visualizaciones(df)
    print("Visualizaciones generadas:")
    for name, path in paths.items():
        print(f"  - {name}: {path}")
