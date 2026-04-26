-- Tabela Gold: preferências de aposta por cliente
-- Consumida por: dashboard (preferências), agente (perguntas de comportamento)
CREATE TABLE IF NOT EXISTS gold.betting_preferences (
    customer_id          INTEGER PRIMARY KEY,
    preferred_channel    VARCHAR(50),
    preferred_market     VARCHAR(100),
    preferred_bet_type   VARCHAR(100),
    live_bet_pct         NUMERIC(5,2),
    peak_hour            INTEGER,
    updated_at           TIMESTAMP DEFAULT NOW()
);
