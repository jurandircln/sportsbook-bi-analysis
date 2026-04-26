-- Tabela Bronze: informações de eventos esportivos
-- Fonte: Events.csv
CREATE TABLE IF NOT EXISTS bronze.events (
    event_id         TEXT,
    event_sport_name TEXT,
    event_class_name TEXT,
    event_type_name  TEXT,
    event_name       TEXT,
    event_start_time TEXT,
    event_end_time   TEXT,
    ingested_at      TIMESTAMP DEFAULT NOW()
);
