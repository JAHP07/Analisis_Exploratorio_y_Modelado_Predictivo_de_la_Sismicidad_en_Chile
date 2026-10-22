"""CLI para cargar eventos USGS a PostgreSQL con UPSERT incremental.

Ejemplo:
python -m scripts.cargar_sismos_postgres --desde 2026-09-01 --hasta 2026-09-30
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from src.etl_postgres import (
    aplicar_esquema,
    cargar_eventos,
    consultar_usgs,
    normalizar_eventos,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Carga sismos de USGS en PostgreSQL local")
    parser.add_argument("--desde", required=True, help="Fecha inicial YYYY-MM-DD")
    parser.add_argument("--hasta", required=True, help="Fecha final YYYY-MM-DD")
    parser.add_argument("--magnitud-minima", type=float, default=4.0)
    args = parser.parse_args()

    # Permite .env de usuario sin subir credenciales al repositorio.
    load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
    clave = os.getenv("POSTGRES_PASSWORD")
    if not clave or clave == "CAMBIAR_ESTA_CLAVE":
        parser.error("Define una contraseña real en .env (POSTGRES_PASSWORD)")

    documento = consultar_usgs(args.desde, args.hasta, args.magnitud_minima)
    eventos, descartados = normalizar_eventos(documento)

    # psycopg se importa aquí para mantener los tests unitarios sin servidor PostgreSQL.
    import psycopg

    with psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "sismicidad"),
        user=os.getenv("POSTGRES_USER", "sismo_user"),
        password=clave,
        connect_timeout=10,
    ) as conexion:
        aplicar_esquema(conexion)
        enviados = cargar_eventos(conexion, eventos)

    print(f"USGS reportó {len(documento['features'])} eventos")
    print(f"Eventos descartados por datos inválidos: {descartados}")
    print(f"Eventos procesados para UPSERT: {enviados}")
    print("Carga completada. Repetir el período no duplica identificadores USGS.")


if __name__ == "__main__":
    main()
