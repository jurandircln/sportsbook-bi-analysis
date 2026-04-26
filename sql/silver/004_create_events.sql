-- Tabela Silver: eventos com tipos corretos
-- Fonte: bronze.events
CREATE TABLE IF NOT EXISTS silver.events (
    event_id    INTEGER PRIMARY KEY,
    sport_name  VARCHAR(100),
    class_name  VARCHAR(100),
    type_name   VARCHAR(100),
    event_name  VARCHAR(255),
    start_time  TIMESTAMP,
    end_time    TIMESTAMP,
    ingested_at TIMESTAMP DEFAULT NOW()
);
