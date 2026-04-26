-- Tabela Gold: performance agregada por nível CRM
-- Consumida por: dashboard (visão por CRM), agente (perguntas por nível)
CREATE TABLE IF NOT EXISTS gold.crm_performance (
    crm_level                      VARCHAR(50) PRIMARY KEY,
    customer_count                 INTEGER,
    total_bets                     INTEGER,
    total_turnover                 NUMERIC(12,2),
    total_winnings                 NUMERIC(12,2),
    gross_revenue                  NUMERIC(12,2),
    avg_bets_per_customer          NUMERIC(10,2),
    avg_turnover_per_customer      NUMERIC(12,2),
    avg_gross_revenue_per_customer NUMERIC(12,2),
    updated_at                     TIMESTAMP DEFAULT NOW()
);
