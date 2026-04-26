-- Tabela Silver: níveis CRM mensais com forward-fill aplicado
-- Regra de negócio: para meses sem registro, usar o nível mais recente atribuído.
-- Exemplo: Bronze em Out/18 e Silver em Jan/19 → Nov e Dez/18 são Bronze.
-- Fonte: bronze.customer_crm_level
CREATE TABLE IF NOT EXISTS silver.customer_crm_level (
    customer_id  INTEGER  NOT NULL,
    year_month   DATE     NOT NULL,
    crm_level    VARCHAR(50) NOT NULL,
    ingested_at  TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (customer_id, year_month)
);
