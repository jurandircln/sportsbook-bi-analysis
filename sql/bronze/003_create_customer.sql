-- Tabela Bronze: base de clientes
-- Fonte: Customer.csv
CREATE TABLE IF NOT EXISTS bronze.customer (
    customer_id              TEXT,
    customer_datecreation_id TEXT,
    customer_gender_name     TEXT,
    customer_birthday        TEXT,
    ingested_at              TIMESTAMP DEFAULT NOW()
);
