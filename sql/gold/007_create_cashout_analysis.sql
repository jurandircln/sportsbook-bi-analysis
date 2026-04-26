-- Tabela Gold: análise mensal de adoção e performance do cash out
-- Cash out foi funcionalidade nova introduzida na temporada
-- Consumida por: dashboard (análise de cash out), agente
CREATE TABLE IF NOT EXISTS gold.cashout_analysis (
    month                 DATE         PRIMARY KEY,
    total_attempts        INTEGER,
    successful_attempts   INTEGER,
    failed_attempts       INTEGER,
    success_rate          NUMERIC(5,2),
    total_cashout_amount  NUMERIC(12,2),
    avg_cashout_amount    NUMERIC(12,2),
    updated_at            TIMESTAMP DEFAULT NOW()
);
