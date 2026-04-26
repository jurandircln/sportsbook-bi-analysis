-- Tabela Gold: segmentação dos clientes na temporada
-- Segmentos:
--   novo       = primeira aposta ocorreu durante a temporada (Set/2018–Ago/2019)
--   existente  = apostas antes E durante a temporada
--   saindo     = apostas antes da temporada, sem apostas nos últimos 3 meses dela
-- Consumida por: dashboard (comportamento da base), agente (perguntas de segmentação)
CREATE TABLE IF NOT EXISTS gold.customer_segments (
    customer_id     INTEGER PRIMARY KEY,
    segment         VARCHAR(20) NOT NULL,
    first_bet_date  DATE,
    last_bet_date   DATE,
    crm_level       VARCHAR(50),
    updated_at      TIMESTAMP DEFAULT NOW()
);
