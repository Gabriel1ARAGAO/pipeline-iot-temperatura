-- ═══════════════════════════════════════════════════════════════
-- VIEWS SQL - Pipeline IoT de Temperatura
-- ═══════════════════════════════════════════════════════════════

-- VIEW 1: Temperatura média por dispositivo
-- Propósito: Identificar quais sensores registram temperaturas
-- mais altas ou mais baixas em média, útil para detectar
-- anomalias ou sensores mal posicionados.
CREATE OR REPLACE VIEW avg_temp_por_dispositivo AS
SELECT
    device_id,
    ROUND(AVG(temperature)::numeric, 2) AS avg_temp,
    COUNT(*) AS total_leituras
FROM temperature_readings
GROUP BY device_id
ORDER BY avg_temp DESC;

-- VIEW 2: Leituras por hora do dia
-- Propósito: Revelar padrões de comportamento térmico ao longo
-- do dia — picos no período da tarde, quedas à madrugada —
-- auxiliando no planejamento de sistemas de climatização.
CREATE OR REPLACE VIEW leituras_por_hora AS
SELECT
    EXTRACT(HOUR FROM reading_time) AS hora,
    COUNT(*) AS contagem,
    ROUND(AVG(temperature)::numeric, 2) AS temp_media
FROM temperature_readings
GROUP BY hora
ORDER BY hora;

-- VIEW 3: Temperatura máxima, mínima e média por dia
-- Propósito: Acompanhar a variação térmica diária, detectar
-- eventos extremos de temperatura e analisar tendências
-- ao longo do período monitorado.
CREATE OR REPLACE VIEW temp_max_min_por_dia AS
SELECT
    DATE(reading_time) AS data,
    MAX(temperature)   AS temp_max,
    MIN(temperature)   AS temp_min,
    ROUND(AVG(temperature)::numeric, 2) AS temp_media
FROM temperature_readings
GROUP BY DATE(reading_time)
ORDER BY data;