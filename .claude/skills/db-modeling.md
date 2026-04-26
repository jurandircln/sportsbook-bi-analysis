# Skill: db-modeling

Use esta skill ao criar ou evoluir qualquer tabela, schema ou índice no banco de dados.

## Checklist obrigatório

- [ ] Consultar o ADR-002 (`docs/technical-context/adr/ADR-002-database-modeling.md`)
      para garantir aderência às decisões de modelagem já tomadas
- [ ] Verificar se a tabela já existe no catálogo de dados
      (`docs/technical-context/data-catalog/`)
- [ ] Definir a camada correta (Bronze, Silver ou Gold) e o propósito da tabela
- [ ] Usar TEXT para todas as colunas de tabelas Bronze
- [ ] Usar tipos precisos nas tabelas Silver:
      - IDs: INTEGER
      - Datas sem hora: DATE
      - Timestamps: TIMESTAMP
      - Valores monetários: NUMERIC(12,2)
      - Flags: BOOLEAN
      - Textos curtos: VARCHAR(N)
- [ ] Incluir coluna `ingested_at TIMESTAMP DEFAULT NOW()` em Bronze e Silver
- [ ] Incluir coluna `updated_at TIMESTAMP DEFAULT NOW()` em Gold
- [ ] Adicionar índices nas colunas usadas em JOINs e filtros frequentes
- [ ] Criar o DDL correspondente em `sql/<camada>/NNN_descricao.sql`
- [ ] Atualizar `docker/init.sql` com o novo DDL
- [ ] Atualizar o catálogo de dados (invocar skill `update-data-catalog`)
- [ ] Se a decisão for nova ou divergir do padrão, criar ADR (invocar skill `create-adr`)
- [ ] Em tabelas Silver, identificar se a tabela é FATO ou DIMENSÃO (Star Schema — ADR-006)
- [ ] Tabelas fato: nomenclatura silver.fact_<nome>, incluir medidas e FKs para dimensões
- [ ] Tabelas dimensão: nomenclatura silver.dim_<nome>
      - Usar chave natural (INTEGER) quando o ID original é estável
      - Usar surrogate key (SERIAL) quando o valor original é texto livre
- [ ] dim_date: não duplicar — verificar se o período já está coberto antes de recriar
- [ ] FKs em fact_*: criar índices em todas as colunas de FK

## Padrão de nomenclatura SQL

- Schemas: `bronze`, `silver`, `gold`
- Tabelas: `snake_case` (ex: `customer_crm_level`)
- Colunas: `snake_case` (ex: `gross_revenue`)
- Índices: `idx_<schema>_<tabela>_<coluna>` (ex: `idx_silver_fact_bets_customer`)
- PKs: declaradas inline na coluna quando simples, ou como constraint quando composta

## Template de DDL Bronze

```sql
-- Tabela Bronze: <descrição>
-- Fonte: <arquivo CSV de origem>
CREATE TABLE IF NOT EXISTS bronze.<nome> (
    <coluna_id>  TEXT,
    <coluna_2>   TEXT,
    ...
    ingested_at  TIMESTAMP DEFAULT NOW()
);
```

## Template de DDL Silver

> ⚠️ **Obsoleto após ADR-006.** Use os templates de Tabela Fato ou Dimensão abaixo.
> Não criar tabelas Silver sem prefixo `fact_` ou `dim_`.

## Template de DDL Gold

```sql
-- Tabela Gold: <descrição>
-- Consumida por: <dashboard / agente / ambos>
CREATE TABLE IF NOT EXISTS gold.<nome> (
    <id>         <TIPO> PRIMARY KEY,
    <metrica_1>  NUMERIC(12,2),
    ...
    updated_at   TIMESTAMP DEFAULT NOW()
);
```

## Template de DDL Silver — Tabela Fato

```sql
-- Tabela Fato Silver: <descrição>
-- Grão: <uma linha por X>
-- Regras de negócio aplicadas: <listar>
-- Fonte: bronze.<origem>
CREATE TABLE IF NOT EXISTS silver.fact_<nome> (
    <id>            TEXT          PRIMARY KEY,
    <dim_fk>_id     INTEGER       NOT NULL,    -- FK → silver.dim_<nome>
    <medida>        NUMERIC(12,2) NOT NULL,
    <dim_degenera>  VARCHAR(N),               -- dimensão degenerada (sem tabela própria)
    ingested_at     TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_silver_fact_<nome>_<dim>
    ON silver.fact_<nome> (<dim_fk>_id);
```

## Template de DDL Silver — Dimensão com Chave Natural

```sql
-- Tabela Dimensão Silver: <descrição>
-- Chave natural: <id> (INTEGER estável)
-- Fonte: bronze.<origem>
CREATE TABLE IF NOT EXISTS silver.dim_<nome> (
    <natural_id>  INTEGER     PRIMARY KEY,
    <atributo_1>  VARCHAR(N),
    ingested_at   TIMESTAMP DEFAULT NOW()
);
```

## Template de DDL Silver — Dimensão com Surrogate Key

```sql
-- Tabela Dimensão Silver: <descrição>
-- Surrogate key (SERIAL): valor original é texto livre sem unicidade estável.
-- Fonte: bronze.<origem>
CREATE TABLE IF NOT EXISTS silver.dim_<nome> (
    <surrogate_id>  SERIAL      PRIMARY KEY,
    <atributo_1>    VARCHAR(N)  NOT NULL,
    ingested_at     TIMESTAMP DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_silver_dim_<nome>_unique
    ON silver.dim_<nome> (<atributo_1>);
```
