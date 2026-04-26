-- Tabela Silver: clientes com tipos corretos e idade calculada
-- Fonte: bronze.customer
CREATE TABLE IF NOT EXISTS silver.customer (
    customer_id        INTEGER PRIMARY KEY,
    registration_date  DATE NOT NULL,
    gender             VARCHAR(20),
    birth_date         DATE,
    age                INTEGER,
    ingested_at        TIMESTAMP DEFAULT NOW()
);
