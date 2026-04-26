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

## Padrão de nomenclatura SQL

- Schemas: `bronze`, `silver`, `gold`
- Tabelas: `snake_case` (ex: `customer_crm_level`)
- Colunas: `snake_case` (ex: `gross_revenue`)
- Índices: `idx_<schema>_<tabela>_<coluna>` (ex: `idx_silver_sportsbook_customer`)
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

```sql
-- Tabela Silver: <descrição>
-- Regras de negócio aplicadas: <listar regras>
-- Fonte: bronze.<tabela_origem>
CREATE TABLE IF NOT EXISTS silver.<nome> (
    <id>         INTEGER PRIMARY KEY,
    <coluna_2>   <TIPO> NOT NULL,
    ...
    ingested_at  TIMESTAMP DEFAULT NOW()
);
```

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
