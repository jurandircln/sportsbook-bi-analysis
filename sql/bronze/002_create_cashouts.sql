-- Tabela Bronze: tentativas de cash out
-- Fonte: Cashouts.csv
-- Todas as colunas em TEXT para preservar dado original sem risco de cast
CREATE TABLE IF NOT EXISTS bronze.cashouts (
    cashout_attempt_bet_id          TEXT,
    cashout_attempt_bet_cashout_id  TEXT,
    cashout_attempt_bet_cashout_created TEXT,
    cashout_attempt_bet_cashout_status  TEXT,
    cashout_attempt_cashout_amount      TEXT,
    ingested_at                         TIMESTAMP DEFAULT NOW()
);
