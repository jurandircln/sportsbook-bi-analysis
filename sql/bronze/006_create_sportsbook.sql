-- Tabela Bronze: atividade de apostas
-- Fonte: Sportsbook.csv
-- KPI principal: Gross Revenue = Turnover - Winnings (calculado na Silver)
CREATE TABLE IF NOT EXISTS bronze.sportsbook (
    sportbetsettled_bet_id      TEXT,
    bettype_name                TEXT,
    market_template_name        TEXT,
    sportbetsettled_customer_id TEXT,
    sportbetsettled_settled     TEXT,
    sportbetsettled_placed      TEXT,
    channel_name                TEXT,
    sportbetsettled_event_id    TEXT,
    turnover                    TEXT,
    winnings                    TEXT,
    ingested_at                 TIMESTAMP DEFAULT NOW()
);
