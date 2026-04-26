-- Tabela Gold: KPIs de performance por cliente na temporada
-- Consumida por: dashboard (visão de clientes), agente (perguntas de performance)
CREATE TABLE IF NOT EXISTS gold.customer_performance (
    customer_id          INTEGER PRIMARY KEY,
    gender               VARCHAR(20),
    age                  INTEGER,
    total_bets           INTEGER,
    total_turnover       NUMERIC(12,2),
    total_winnings       NUMERIC(12,2),
    gross_revenue        NUMERIC(12,2),
    live_bets            INTEGER,
    pre_event_bets       INTEGER,
    cashout_attempts     INTEGER,
    successful_cashouts  INTEGER,
    updated_at           TIMESTAMP DEFAULT NOW()
);
