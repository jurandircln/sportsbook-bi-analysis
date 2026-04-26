-- Tabela Dimensão Silver: cliente
-- Chave natural: customer_id (INTEGER estável)
-- Fonte: bronze.customer
CREATE TABLE IF NOT EXISTS silver.dim_customer (
    customer_id        INTEGER   PRIMARY KEY,
    registration_date  DATE      NOT NULL,
    gender             VARCHAR(20),
    birth_date         DATE,
    age                INTEGER,
    ingested_at        TIMESTAMP DEFAULT NOW()
);
