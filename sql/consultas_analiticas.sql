-- Consultas SQL para práctica de Analista de Datos JR.
-- Tabla: eventos_sismicos (fechas almacenadas en UTC).

-- 1. Indicadores generales de los eventos cargados.
SELECT COUNT(*) AS total_eventos,
       ROUND(AVG(magnitud)::numeric, 2) AS magnitud_promedio,
       MAX(magnitud) AS magnitud_maxima,
       ROUND(AVG(profundidad_km)::numeric, 1) AS profundidad_media_km
FROM eventos_sismicos;

-- 2. Actividad por mes (hora local de Chile).
SELECT DATE_TRUNC('month', fecha AT TIME ZONE 'America/Santiago')::date AS mes,
       COUNT(*) AS cantidad_sismos
FROM eventos_sismicos
GROUP BY 1
ORDER BY mes DESC;

-- 3. Los 10 mayores sismos del conjunto almacenado.
SELECT fecha AT TIME ZONE 'America/Santiago' AS fecha_chile,
       lugar, magnitud, profundidad_km
FROM eventos_sismicos
ORDER BY magnitud DESC, fecha DESC
LIMIT 10;

-- 4. Bandas de magnitud para informes.
SELECT CASE
         WHEN magnitud >= 6 THEN '6.0 o superior'
         WHEN magnitud >= 5 THEN '5.0 a 5.9'
         ELSE 'menor a 5.0'
       END AS banda_magnitud,
       COUNT(*) AS eventos
FROM eventos_sismicos
GROUP BY 1
ORDER BY banda_magnitud;

-- 5. Eventos por nivel de profundidad.
SELECT CASE
         WHEN profundidad_km < 70 THEN 'Superficial'
         WHEN profundidad_km < 300 THEN 'Intermedio'
         ELSE 'Profundo'
       END AS categoria_profundidad,
       COUNT(*) AS cantidad,
       ROUND(AVG(magnitud)::numeric, 2) AS magnitud_media
FROM eventos_sismicos
GROUP BY 1
ORDER BY cantidad DESC;

-- 6. Actividad semanal (semanas iniciadas el lunes, hora de Chile).
SELECT DATE_TRUNC('week', fecha AT TIME ZONE 'America/Santiago')::date AS semana_inicio,
       COUNT(*) AS eventos
FROM eventos_sismicos
GROUP BY 1
ORDER BY semana_inicio DESC;
