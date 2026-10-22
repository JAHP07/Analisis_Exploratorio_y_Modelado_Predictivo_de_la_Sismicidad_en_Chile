-- Esquema PostgreSQL v1: datos públicos de USGS.
-- Ejecutable varias veces sin borrar datos.
CREATE TABLE IF NOT EXISTS eventos_sismicos (
    id_usgs TEXT PRIMARY KEY,
    fecha TIMESTAMPTZ NOT NULL,
    magnitud DOUBLE PRECISION NOT NULL CHECK (magnitud > 0 AND magnitud <= 10),
    profundidad_km DOUBLE PRECISION NOT NULL CHECK (profundidad_km >= 0),
    latitud DOUBLE PRECISION NOT NULL CHECK (latitud BETWEEN -90 AND 90),
    longitud DOUBLE PRECISION NOT NULL CHECK (longitud BETWEEN -180 AND 180),
    lugar TEXT NOT NULL,
    actualizado_usgs_ms BIGINT NOT NULL DEFAULT 0,
    fecha_ingesta TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sismos_fecha ON eventos_sismicos (fecha DESC);
CREATE INDEX IF NOT EXISTS idx_sismos_magnitud_fecha ON eventos_sismicos (magnitud, fecha DESC);
