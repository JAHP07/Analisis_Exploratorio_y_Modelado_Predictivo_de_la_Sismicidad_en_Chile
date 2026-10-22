# Fase 2 · PostgreSQL y SQL para sismicidad en Chile

Esta etapa se agrega al repositorio existente; **no reemplaza** los notebooks, los gráficos ni el análisis de Python. Es un laboratorio reproducible de extracción (USGS), normalización y carga incremental a PostgreSQL. Se usan observaciones históricas; **no predice terremotos**. El rectángulo geográfico usado corresponde aproximadamente a Chile continental y no incluye todos los territorios insulares.

## Requisitos

- GitHub Codespaces o Linux con Python 3.12 y Docker + Docker Compose disponibles.
- Acceso a internet únicamente para descargar dependencias y consultar la API pública USGS.
- Puerto `5432` libre. El servicio solo se publica en `127.0.0.1`, no en una interfaz pública.

## Primera configuración (Codespaces)

Desde la raíz del repositorio, en la rama de esta funcionalidad:

```bash
cp .env.example .env
# Edita .env y reemplaza CAMBIAR_ESTA_CLAVE por una contraseña larga propia.
python -m pip install -r requirements.txt

docker compose up -d db
docker compose ps
```

El archivo `.env` está ignorado por Git: **no lo subas ni compartas su contenido**. Evita exponer el puerto de PostgreSQL como público en Codespaces. Comprueba primero que `docker compose version` funciona; si no tienes Docker disponible en tu Codespace, prepara otro entorno o instala PostgreSQL localmente antes de continuar.

La inicialización SQL se realiza automáticamente cuando se ejecuta por primera vez el cargador. La base de datos se guarda en el volumen Docker `sismicidad_pg_data` (persistente entre reinicios normales del contenedor). Para eliminar todos los datos de prueba, `docker compose down -v` (acción destructiva).

## Ejecutar el pipeline ETL

```bash
python -m scripts.cargar_sismos_postgres --desde 2026-09-01 --hasta 2026-09-30
```

Opcional:

```bash
python -m scripts.cargar_sismos_postgres --desde 2026-09-01 --hasta 2026-09-07 --magnitud-minima 5.0
```

El cargador verifica fechas, consulta USGS con timeout, conserva la ID oficial (`id_usgs`), transforma fechas a UTC, descarta filas inválidas y escribe con `ON CONFLICT ... DO UPDATE`. **No duplica eventos** si vuelves a ejecutar el mismo período: la tabla tiene clave primaria por ID USGS y solo se actualiza un evento cuando USGS reporta una versión más reciente. El contador `eventos procesados para UPSERT` **no representa altas netas**.

> Para periodos muy grandes, divide la extracción en meses o semanas. El cargador rechaza consultas que alcancen el límite de 20.000 registros de USGS para evitar un conjunto incompleto.

## Consultar desde PostgreSQL

```bash
docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' <<'SQL'
SELECT COUNT(*) AS cantidad FROM eventos_sismicos;
SELECT id_usgs, fecha, magnitud, lugar
FROM eventos_sismicos ORDER BY fecha DESC LIMIT 5;
SQL
```

Para ejecutar las seis consultas de demostración:

```bash
docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < sql/consultas_analiticas.sql
```

Con clientes SQL de escritorio (p. ej. DBeaver) usa host `127.0.0.1`, puerto `5432` (o tu variable `POSTGRES_PORT`), base, usuario y contraseña de `.env`, **solo desde el entorno donde corre Docker**. No compartas tu contraseña.

## Práctica SQL: ejercicios para Analista de Datos Jr.

Comienza con `sql/consultas_analiticas.sql` (incluye respuestas de referencia). Luego resuelve sin mirar:

| Nivel | Ejercicio | Funciones esperadas |
|---|---|---|
| 1 | Encontrar el promedio de magnitud y máximo de profundidad | `AVG`, `MAX`, `ROUND` |
| 1 | Contar sismos con magnitud ≥ 6.0 | `COUNT`, `WHERE` |
| 2 | Contar sismos por mes en horario de Chile | `DATE_TRUNC`, `GROUP BY` |
| 2 | Top 5 de eventos más profundos | `ORDER BY`, `LIMIT` |
| 3 | Comparar cantidad y magnitud media por bandas de profundidad | `CASE`, `COUNT`, `AVG` |
| 3 | Calcular el porcentaje de eventos ≥ 5.0 por mes | `FILTER` o `CASE`, CTE, operaciones con `NULLIF` |

Para análisis responsable, indica siempre el rango temporal, el área consultada y la magnitud mínima en tus resultados; un catálogo filtrado no representa *todos* los sismos ocurridos en Chile.

## Pruebas y calidad

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest tests/ -v
```

Las pruebas unitarias del ETL no requieren PostgreSQL ni conexiones a USGS. La incorporación de esta fase agrega 13 pruebas al conjunto existente. La validación integral de lectura/escritura sí requiere levantar PostgreSQL y ejecutar el cargador con un rango de fechas real.

## Arquitectura

```text
USGS (GeoJSON)
    │
    ▼
src/etl_postgres.py   [validación, ID del evento, UTC, transformaciones]
    │
    ▼
scripts/cargar_sismos_postgres.py  [CLI, conexión local PostgreSQL]
    │
    ▼
PostgreSQL 17 (compose.yaml) → eventos_sismicos → consultas SQL
```

## Próxima fase propuesta

Agregar un dashboard Streamlit que consulte PostgreSQL en modo lectura con filtros de fecha, magnitud y profundidad; mantener el ETL desacoplado de la interfaz.
