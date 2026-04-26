-- Tabela Gold: resumo mensal da temporada
-- Granularidade: 1 linha por mês da temporada (Set/2018 a Ago/2019)
-- Consumida por: dashboard (evolução temporal), agente (visão geral da temporada)
CREATE TABLE IF NOT EXISTS gold.season_summary (
    month              DATE         PRIMARY KEY,
    total_customers    INTEGER,
    new_customers      INTEGER,
    churned_customers  INTEGER,
    total_bets         INTEGER,
    total_turnover     NUMERIC(12,2),
    total_winnings     NUMERIC(12,2),
    gross_revenue      NUMERIC(12,2),
    live_bet_pct       NUMERIC(5,2),
    updated_at         TIMESTAMP DEFAULT NOW()
);
