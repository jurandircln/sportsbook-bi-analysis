# Star Schema Silver + README — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refatorar a camada Silver de tabelas planas para Star Schema (Kimball) com tabelas fato e dimensão, criar ADR-006, atualizar ADR-002 e db-modeling skill, e criar o README.md do projeto.

**Architecture:** 5 DDLs Silver flat são removidos e substituídos por 8 DDLs com prefixos `fact_` e `dim_`. O `docker/init.sql` é regenerado com as dimensões antes das fatos para que as FKs sejam válidas. Toda a documentação de governança (ADRs, skill, README) é atualizada em sequência.

**Tech Stack:** PostgreSQL 16, Docker Compose, SQL DDL puro, Markdown.

**Spec:** `docs/superpowers/specs/2026-04-26-star-schema-silver-readme-design.md`

---

## Mapa de Arquivos

| Ação | Arquivo |
|---|---|
| Deletar | `sql/silver/002_create_customer.sql` |
| Deletar | `sql/silver/003_create_customer_crm_level.sql` |
| Deletar | `sql/silver/004_create_events.sql` |
| Deletar | `sql/silver/005_create_sportsbook.sql` |
| Deletar | `sql/silver/006_create_cashouts.sql` |
| Criar | `sql/silver/002_create_dim_customer.sql` |
| Criar | `sql/silver/003_create_dim_crm_level.sql` |
| Criar | `sql/silver/004_create_dim_event.sql` |
| Criar | `sql/silver/005_create_dim_market.sql` |
| Criar | `sql/silver/006_create_dim_channel.sql` |
| Criar | `sql/silver/007_create_dim_date.sql` |
| Criar | `sql/silver/008_create_fact_bets.sql` |
| Criar | `sql/silver/009_create_fact_cashouts.sql` |
| Modificar | `docker/init.sql` (seção Silver regenerada) |
| Criar | `docs/technical-context/adr/ADR-006-star-schema-silver.md` |
| Modificar | `docs/technical-context/adr/ADR-002-database-modeling.md` (linha de status) |
| Modificar | `.claude/skills/db-modeling.md` (checklist + templates) |
| Criar | `README.md` |

---

### Task 1: Remover DDLs Silver flat

**Files:**
- Delete: `sql/silver/002_create_customer.sql`
- Delete: `sql/silver/003_create_customer_crm_level.sql`
- Delete: `sql/silver/004_create_events.sql`
- Delete: `sql/silver/005_create_sportsbook.sql`
- Delete: `sql/silver/006_create_cashouts.sql`

- [ ] **Step 1: Verificar arquivos existentes**

```bash
ls sql/silver/
```

Esperado: `001_create_schema.sql  002_create_customer.sql  003_create_customer_crm_level.sql  004_create_events.sql  005_create_sportsbook.sql  006_create_cashouts.sql`

- [ ] **Step 2: Remover os 5 DDLs flat**

```bash
rm sql/silver/002_create_customer.sql \
   sql/silver/003_create_customer_crm_level.sql \
   sql/silver/004_create_events.sql \
   sql/silver/005_create_sportsbook.sql \
   sql/silver/006_create_cashouts.sql
```

- [ ] **Step 3: Confirmar remoção**

```bash
ls sql/silver/
```

Esperado: apenas `001_create_schema.sql`

- [ ] **Step 4: Commit**

```bash
git add -A sql/silver/
git commit -m "refactor: remove DDLs Silver flat (substituídos por Star Schema)"
```

---

### Task 2: Criar DDLs Silver — dim_customer e dim_crm_level

**Files:**
- Create: `sql/silver/002_create_dim_customer.sql`
- Create: `sql/silver/003_create_dim_crm_level.sql`

- [ ] **Step 1: Criar `sql/silver/002_create_dim_customer.sql`**

```sql
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
```

- [ ] **Step 2: Criar `sql/silver/003_create_dim_crm_level.sql`**

```sql
-- Tabela Dimensão Silver: nível CRM por cliente por mês (variação temporal)
-- Regra de negócio: forward-fill aplicado — meses sem registro usam o nível mais recente.
-- Para JOIN na análise: customer_id + DATE_TRUNC('month', placed_at) = year_month
-- Fonte: bronze.customer_crm_level
CREATE TABLE IF NOT EXISTS silver.dim_crm_level (
    customer_id  INTEGER     NOT NULL,
    year_month   DATE        NOT NULL,
    crm_level    VARCHAR(50) NOT NULL,
    ingested_at  TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (customer_id, year_month)
);

CREATE INDEX IF NOT EXISTS idx_silver_dim_crm_level_customer
    ON silver.dim_crm_level (customer_id);
CREATE INDEX IF NOT EXISTS idx_silver_dim_crm_level_month
    ON silver.dim_crm_level (year_month);
```

- [ ] **Step 3: Verificar arquivos criados**

```bash
ls sql/silver/
```

Esperado: `001_create_schema.sql  002_create_dim_customer.sql  003_create_dim_crm_level.sql`

- [ ] **Step 4: Commit**

```bash
git add sql/silver/002_create_dim_customer.sql sql/silver/003_create_dim_crm_level.sql
git commit -m "feat: adicionar DDLs Silver dim_customer e dim_crm_level (Star Schema)"
```

---

### Task 3: Criar DDL Silver — dim_event

**Files:**
- Create: `sql/silver/004_create_dim_event.sql`

- [ ] **Step 1: Criar `sql/silver/004_create_dim_event.sql`**

```sql
-- Tabela Dimensão Silver: evento esportivo
-- Chave natural: event_id (INTEGER estável)
-- Fonte: bronze.events
CREATE TABLE IF NOT EXISTS silver.dim_event (
    event_id    INTEGER      PRIMARY KEY,
    sport_name  VARCHAR(100),
    class_name  VARCHAR(100),
    type_name   VARCHAR(100),
    event_name  VARCHAR(255),
    start_time  TIMESTAMP,
    end_time    TIMESTAMP,
    ingested_at TIMESTAMP DEFAULT NOW()
);
```

- [ ] **Step 2: Verificar arquivo criado**

```bash
ls sql/silver/
```

Esperado: `001  002  003  004` presentes.

- [ ] **Step 3: Commit**

```bash
git add sql/silver/004_create_dim_event.sql
git commit -m "feat: adicionar DDL Silver dim_event (Star Schema)"
```

---

### Task 4: Criar DDLs Silver — dim_market e dim_channel

**Files:**
- Create: `sql/silver/005_create_dim_market.sql`
- Create: `sql/silver/006_create_dim_channel.sql`

- [ ] **Step 1: Criar `sql/silver/005_create_dim_market.sql`**

```sql
-- Tabela Dimensão Silver: mercado de aposta
-- Surrogate key (SERIAL): valores originais são texto livre sem unicidade garantida.
-- Dedupado por combinação única de (market_name, bet_type) na transformação.
-- Fonte: bronze.sportsbook
CREATE TABLE IF NOT EXISTS silver.dim_market (
    market_id    SERIAL       PRIMARY KEY,
    market_name  VARCHAR(100) NOT NULL,
    bet_type     VARCHAR(100),
    ingested_at  TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_silver_dim_market_unique
    ON silver.dim_market (market_name, bet_type);
```

- [ ] **Step 2: Criar `sql/silver/006_create_dim_channel.sql`**

```sql
-- Tabela Dimensão Silver: canal de aposta
-- Surrogate key (SERIAL): valores originais são texto livre.
-- Dedupado por channel_name na transformação.
-- Fonte: bronze.sportsbook
CREATE TABLE IF NOT EXISTS silver.dim_channel (
    channel_id    SERIAL      PRIMARY KEY,
    channel_name  VARCHAR(50) NOT NULL,
    ingested_at   TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_silver_dim_channel_unique
    ON silver.dim_channel (channel_name);
```

- [ ] **Step 3: Verificar arquivos criados**

```bash
ls sql/silver/
```

Esperado: `001  002  003  004  005  006` presentes.

- [ ] **Step 4: Commit**

```bash
git add sql/silver/005_create_dim_market.sql sql/silver/006_create_dim_channel.sql
git commit -m "feat: adicionar DDLs Silver dim_market e dim_channel (Star Schema)"
```

---

### Task 5: Criar DDL Silver — dim_date

**Files:**
- Create: `sql/silver/007_create_dim_date.sql`

- [ ] **Step 1: Criar `sql/silver/007_create_dim_date.sql`**

```sql
-- Tabela Dimensão Silver: calendário por dia
-- Granularidade: 1 registro por dia. Gerada na transformação cobrindo o período
-- relevante (Jul/2017 a Set/2019, com margem para apostas pré-temporada).
-- Chave: YYYYMMDD como INTEGER (ex: 20180901).
-- placed_hour permanece em fact_bets como dimensão degenerada (não infla esta tabela).
-- Fonte: gerada programaticamente durante a transformação
CREATE TABLE IF NOT EXISTS silver.dim_date (
    date_id      INTEGER     PRIMARY KEY,
    full_date    DATE        NOT NULL,
    year         INTEGER     NOT NULL,
    month        INTEGER     NOT NULL,
    month_name   VARCHAR(20) NOT NULL,
    day          INTEGER     NOT NULL,
    day_of_week  INTEGER     NOT NULL,
    day_name     VARCHAR(20) NOT NULL,
    is_weekend   BOOLEAN     NOT NULL,
    ingested_at  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_dim_date_full_date
    ON silver.dim_date (full_date);
```

- [ ] **Step 2: Verificar arquivo criado**

```bash
ls sql/silver/
```

Esperado: `001  002  003  004  005  006  007` presentes.

- [ ] **Step 3: Commit**

```bash
git add sql/silver/007_create_dim_date.sql
git commit -m "feat: adicionar DDL Silver dim_date (Star Schema)"
```

---

### Task 6: Criar DDLs Silver — fact_bets e fact_cashouts

**Files:**
- Create: `sql/silver/008_create_fact_bets.sql`
- Create: `sql/silver/009_create_fact_cashouts.sql`

- [ ] **Step 1: Criar `sql/silver/008_create_fact_bets.sql`**

```sql
-- Tabela Fato Silver: apostas liquidadas
-- Grão: 1 linha por aposta
-- Regras de negócio aplicadas:
--   gross_revenue = turnover - winnings
--   is_live = placed_at >= event_start_time (via JOIN com dim_event na transformação)
--   placed_hour: dimensão degenerada (EXTRACT(HOUR FROM placed_at))
-- Fonte: bronze.sportsbook + silver.dim_event (para is_live)
CREATE TABLE IF NOT EXISTS silver.fact_bets (
    bet_id        TEXT          PRIMARY KEY,
    customer_id   INTEGER       NOT NULL,
    event_id      INTEGER,
    date_id       INTEGER       NOT NULL,
    market_id     INTEGER,
    channel_id    INTEGER,
    placed_at     TIMESTAMP     NOT NULL,
    settled_at    TIMESTAMP,
    placed_hour   INTEGER,
    turnover      NUMERIC(12,2) NOT NULL,
    winnings      NUMERIC(12,2) NOT NULL,
    gross_revenue NUMERIC(12,2) NOT NULL,
    is_live       BOOLEAN       NOT NULL,
    ingested_at   TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_fact_bets_customer
    ON silver.fact_bets (customer_id);
CREATE INDEX IF NOT EXISTS idx_silver_fact_bets_event
    ON silver.fact_bets (event_id);
CREATE INDEX IF NOT EXISTS idx_silver_fact_bets_date
    ON silver.fact_bets (date_id);
CREATE INDEX IF NOT EXISTS idx_silver_fact_bets_placed_at
    ON silver.fact_bets (placed_at);
```

- [ ] **Step 2: Criar `sql/silver/009_create_fact_cashouts.sql`**

```sql
-- Tabela Fato Silver: tentativas de cash out
-- Grão: 1 linha por tentativa de cash out
-- bet_id e status são dimensões degeneradas (sem tabela própria).
-- Fonte: bronze.cashouts
CREATE TABLE IF NOT EXISTS silver.fact_cashouts (
    cashout_id      TEXT          PRIMARY KEY,
    bet_id          TEXT          NOT NULL,
    date_id         INTEGER       NOT NULL,
    created_at      TIMESTAMP     NOT NULL,
    status          VARCHAR(50)   NOT NULL,
    cashout_amount  NUMERIC(12,2),
    ingested_at     TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_fact_cashouts_bet
    ON silver.fact_cashouts (bet_id);
CREATE INDEX IF NOT EXISTS idx_silver_fact_cashouts_date
    ON silver.fact_cashouts (date_id);
```

- [ ] **Step 3: Verificar arquivos criados**

```bash
ls sql/silver/
```

Esperado: `001  002  003  004  005  006  007  008  009` — total de 9 arquivos.

- [ ] **Step 4: Commit**

```bash
git add sql/silver/008_create_fact_bets.sql sql/silver/009_create_fact_cashouts.sql
git commit -m "feat: adicionar DDLs Silver fact_bets e fact_cashouts (Star Schema)"
```

---

### Task 7: Regenerar docker/init.sql — seção Silver

**Files:**
- Modify: `docker/init.sql` (substituir seção Silver, linhas 82–164)

A seção Silver do `docker/init.sql` deve ser completamente substituída pelos 8 novos DDLs do Star Schema. Bronze e Gold permanecem sem alteração. A ordem dos DDLs deve ser: `001_create_schema` → dimensões (002–007) → fatos (008–009), garantindo que FKs lógicas sejam respeitadas.

- [ ] **Step 1: Ler o arquivo atual para identificar os limites exatos da seção Silver**

```bash
grep -n "CAMADA SILVER\|CAMADA GOLD" docker/init.sql
```

Esperado: linhas apontando para o início da seção Silver e o início da seção Gold.

- [ ] **Step 2: Substituir a seção Silver no `docker/init.sql`**

Localizar o bloco entre os comentários `-- CAMADA SILVER` e `-- CAMADA GOLD` e substituir por:

```sql
-- =============================================================================
-- CAMADA SILVER — Star Schema (Kimball)
-- Dados limpos, tipados e com regras de negócio aplicadas
-- Estrutura: tabelas dimensão (dim_*) seguidas de tabelas fato (fact_*)
-- Dimensões devem ser criadas antes dos fatos (FKs lógicas)
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS silver;

-- Dimensão: cliente
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

-- Dimensão: nível CRM por cliente por mês (variação temporal)
-- Regra de negócio: forward-fill aplicado — meses sem registro usam o nível mais recente.
-- Para JOIN na análise: customer_id + DATE_TRUNC('month', placed_at) = year_month
-- Fonte: bronze.customer_crm_level
CREATE TABLE IF NOT EXISTS silver.dim_crm_level (
    customer_id  INTEGER     NOT NULL,
    year_month   DATE        NOT NULL,
    crm_level    VARCHAR(50) NOT NULL,
    ingested_at  TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (customer_id, year_month)
);

CREATE INDEX IF NOT EXISTS idx_silver_dim_crm_level_customer
    ON silver.dim_crm_level (customer_id);
CREATE INDEX IF NOT EXISTS idx_silver_dim_crm_level_month
    ON silver.dim_crm_level (year_month);

-- Dimensão: evento esportivo
-- Chave natural: event_id (INTEGER estável)
-- Fonte: bronze.events
CREATE TABLE IF NOT EXISTS silver.dim_event (
    event_id    INTEGER      PRIMARY KEY,
    sport_name  VARCHAR(100),
    class_name  VARCHAR(100),
    type_name   VARCHAR(100),
    event_name  VARCHAR(255),
    start_time  TIMESTAMP,
    end_time    TIMESTAMP,
    ingested_at TIMESTAMP DEFAULT NOW()
);

-- Dimensão: mercado de aposta
-- Surrogate key (SERIAL): valores originais são texto livre sem unicidade garantida.
-- Dedupado por combinação única de (market_name, bet_type) na transformação.
-- Fonte: bronze.sportsbook
CREATE TABLE IF NOT EXISTS silver.dim_market (
    market_id    SERIAL       PRIMARY KEY,
    market_name  VARCHAR(100) NOT NULL,
    bet_type     VARCHAR(100),
    ingested_at  TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_silver_dim_market_unique
    ON silver.dim_market (market_name, bet_type);

-- Dimensão: canal de aposta
-- Surrogate key (SERIAL): valores originais são texto livre.
-- Dedupado por channel_name na transformação.
-- Fonte: bronze.sportsbook
CREATE TABLE IF NOT EXISTS silver.dim_channel (
    channel_id    SERIAL      PRIMARY KEY,
    channel_name  VARCHAR(50) NOT NULL,
    ingested_at   TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_silver_dim_channel_unique
    ON silver.dim_channel (channel_name);

-- Dimensão: calendário por dia
-- Granularidade: 1 registro por dia. Gerada na transformação cobrindo o período
-- relevante (Jul/2017 a Set/2019, com margem para apostas pré-temporada).
-- Chave: YYYYMMDD como INTEGER (ex: 20180901).
-- placed_hour permanece em fact_bets como dimensão degenerada (não infla esta tabela).
-- Fonte: gerada programaticamente durante a transformação
CREATE TABLE IF NOT EXISTS silver.dim_date (
    date_id      INTEGER     PRIMARY KEY,
    full_date    DATE        NOT NULL,
    year         INTEGER     NOT NULL,
    month        INTEGER     NOT NULL,
    month_name   VARCHAR(20) NOT NULL,
    day          INTEGER     NOT NULL,
    day_of_week  INTEGER     NOT NULL,
    day_name     VARCHAR(20) NOT NULL,
    is_weekend   BOOLEAN     NOT NULL,
    ingested_at  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_dim_date_full_date
    ON silver.dim_date (full_date);

-- Fato: apostas liquidadas
-- Grão: 1 linha por aposta
-- Regras de negócio aplicadas:
--   gross_revenue = turnover - winnings
--   is_live = placed_at >= event_start_time (via JOIN com dim_event na transformação)
--   placed_hour: dimensão degenerada (EXTRACT(HOUR FROM placed_at))
-- Fonte: bronze.sportsbook + silver.dim_event (para is_live)
CREATE TABLE IF NOT EXISTS silver.fact_bets (
    bet_id        TEXT          PRIMARY KEY,
    customer_id   INTEGER       NOT NULL,
    event_id      INTEGER,
    date_id       INTEGER       NOT NULL,
    market_id     INTEGER,
    channel_id    INTEGER,
    placed_at     TIMESTAMP     NOT NULL,
    settled_at    TIMESTAMP,
    placed_hour   INTEGER,
    turnover      NUMERIC(12,2) NOT NULL,
    winnings      NUMERIC(12,2) NOT NULL,
    gross_revenue NUMERIC(12,2) NOT NULL,
    is_live       BOOLEAN       NOT NULL,
    ingested_at   TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_fact_bets_customer
    ON silver.fact_bets (customer_id);
CREATE INDEX IF NOT EXISTS idx_silver_fact_bets_event
    ON silver.fact_bets (event_id);
CREATE INDEX IF NOT EXISTS idx_silver_fact_bets_date
    ON silver.fact_bets (date_id);
CREATE INDEX IF NOT EXISTS idx_silver_fact_bets_placed_at
    ON silver.fact_bets (placed_at);

-- Fato: tentativas de cash out
-- Grão: 1 linha por tentativa de cash out
-- bet_id e status são dimensões degeneradas (sem tabela própria).
-- Fonte: bronze.cashouts
CREATE TABLE IF NOT EXISTS silver.fact_cashouts (
    cashout_id      TEXT          PRIMARY KEY,
    bet_id          TEXT          NOT NULL,
    date_id         INTEGER       NOT NULL,
    created_at      TIMESTAMP     NOT NULL,
    status          VARCHAR(50)   NOT NULL,
    cashout_amount  NUMERIC(12,2),
    ingested_at     TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_silver_fact_cashouts_bet
    ON silver.fact_cashouts (bet_id);
CREATE INDEX IF NOT EXISTS idx_silver_fact_cashouts_date
    ON silver.fact_cashouts (date_id);
```

- [ ] **Step 3: Validar a integridade do init.sql**

```bash
grep -c "CREATE TABLE" docker/init.sql
```

Esperado: `19` (5 bronze + 8 silver + 6 gold)

```bash
grep "CREATE TABLE" docker/init.sql
```

Esperado: bronze.cashouts, bronze.customer, bronze.customer_crm_level, bronze.events, bronze.sportsbook, silver.dim_customer, silver.dim_crm_level, silver.dim_event, silver.dim_market, silver.dim_channel, silver.dim_date, silver.fact_bets, silver.fact_cashouts, gold.customer_performance, gold.customer_segments, gold.betting_preferences, gold.crm_performance, gold.season_summary, gold.cashout_analysis

- [ ] **Step 4: Testar o init.sql no PostgreSQL**

```bash
docker compose down -v
docker compose up -d postgres
sleep 5
docker compose exec postgres psql -U sportsbook -d sportsbook_db -c "\dt silver.*"
```

Esperado: 8 tabelas silver listadas — dim_channel, dim_crm_level, dim_customer, dim_date, dim_event, dim_market, fact_bets, fact_cashouts

- [ ] **Step 5: Verificar índices criados**

```bash
docker compose exec postgres psql -U sportsbook -d sportsbook_db -c "\di silver.*"
```

Esperado: índices idx_silver_* listados para todas as tabelas com FKs.

- [ ] **Step 6: Commit**

```bash
git add docker/init.sql
git commit -m "refactor: regenerar init.sql com Silver Star Schema (8 tabelas fact/dim)"
```

---

### Task 8: Criar ADR-006 — Star Schema na Silver

**Files:**
- Create: `docs/technical-context/adr/ADR-006-star-schema-silver.md`

- [ ] **Step 1: Criar `docs/technical-context/adr/ADR-006-star-schema-silver.md`**

```markdown
# ADR-006: Adoção de Star Schema na Camada Silver

**Data:** 2026-04-26
**Status:** Aceita
**Substitui parcialmente:** ADR-002 (seção "Camada Silver")

## Contexto

A modelagem inicial da Silver (ADR-002) usava tabelas planas sem distinção entre
entidades analíticas. Para suportar queries analíticas eficientes no dashboard e no
agente de BI, e para tornar explícita a separação entre medidas e atributos, é
necessário um modelo dimensional estruturado.

## Decisão

Adotar Star Schema (Kimball) na camada Silver com:
- Tabelas fato: fact_bets, fact_cashouts
- Tabelas dimensão: dim_customer, dim_event, dim_date, dim_market, dim_channel, dim_crm_level

dim_crm_level mantida como dimensão separada com granularidade mensal (Option B),
referenciada via JOIN por customer_id + mês truncado da aposta.

dim_date com granularidade de dia; placed_hour mantido em fact_bets como
dimensão degenerada para análise de horário de pico sem inflar a dimensão.

dim_market e dim_channel usam surrogate key (SERIAL) pois os valores originais
são texto livre sem garantia de unicidade estável.

## Consequências

Queries analíticas no dashboard e no agente ficam mais expressivas e performáticas.
O modelo é autodocumentado — fatos têm medidas, dimensões têm atributos.
A transformação Bronze→Silver fica ligeiramente mais complexa (dedupagem de dim_market
e dim_channel, geração de dim_date). Aceita-se esse custo em troca de um modelo
analítico robusto e escalável.
```

- [ ] **Step 2: Verificar arquivo criado**

```bash
ls docs/technical-context/adr/
```

Esperado: `ADR-001-*.md  ADR-002-*.md  ADR-003-*.md  ADR-004-*.md  ADR-005-*.md  ADR-006-star-schema-silver.md`

- [ ] **Step 3: Commit**

```bash
git add docs/technical-context/adr/ADR-006-star-schema-silver.md
git commit -m "docs: criar ADR-006 — adoção de Star Schema na Silver"
```

---

### Task 9: Atualizar ADR-002 — status parcialmente substituído

**Files:**
- Modify: `docs/technical-context/adr/ADR-002-database-modeling.md` (linha 4)

- [ ] **Step 1: Verificar a linha de status atual no ADR-002**

```bash
grep -n "Status" docs/technical-context/adr/ADR-002-database-modeling.md
```

Esperado: `4: **Status:** Aceita`

- [ ] **Step 2: Atualizar a linha de status**

Localizar a linha:
```
**Status:** Aceita
```

Substituir por:
```
**Status:** Aceita (seção Silver parcialmente substituída por ADR-006)
```

- [ ] **Step 3: Verificar a alteração**

```bash
grep "Status" docs/technical-context/adr/ADR-002-database-modeling.md
```

Esperado: `**Status:** Aceita (seção Silver parcialmente substituída por ADR-006)`

- [ ] **Step 4: Commit**

```bash
git add docs/technical-context/adr/ADR-002-database-modeling.md
git commit -m "docs: atualizar status ADR-002 — Silver substituída por ADR-006"
```

---

### Task 10: Atualizar skill db-modeling com checklist e templates Star Schema

**Files:**
- Modify: `.claude/skills/db-modeling.md`

- [ ] **Step 1: Ler o arquivo atual para localizar pontos de inserção**

```bash
cat -n .claude/skills/db-modeling.md
```

Identificar: (a) o final da seção `## Checklist obrigatório`, (b) o final do arquivo onde ficam os templates.

- [ ] **Step 2: Adicionar novos itens ao checklist**

Após a linha `- [ ] Se a decisão for nova ou divergir do padrão, criar ADR (invocar skill \`create-adr\`)`, adicionar:

```markdown
- [ ] Em tabelas Silver, identificar se a tabela é FATO ou DIMENSÃO (Star Schema — ADR-006)
- [ ] Tabelas fato: nomenclatura silver.fact_<nome>, incluir medidas e FKs para dimensões
- [ ] Tabelas dimensão: nomenclatura silver.dim_<nome>
      - Usar chave natural (INTEGER) quando o ID original é estável
      - Usar surrogate key (SERIAL) quando o valor original é texto livre
- [ ] dim_date: não duplicar — verificar se o período já está coberto antes de recriar
- [ ] FKs em fact_*: criar índices em todas as colunas de FK
```

- [ ] **Step 3: Adicionar templates Fato e Dimensão ao final do arquivo**

Após o `## Template de DDL Gold`, adicionar:

```markdown
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
```

- [ ] **Step 4: Verificar o arquivo atualizado**

```bash
grep -n "FATO\|DIMENSÃO\|surrogate\|fact_\|dim_" .claude/skills/db-modeling.md
```

Esperado: linhas referenciando os novos itens de checklist e os novos templates.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/db-modeling.md
git commit -m "docs: atualizar skill db-modeling com checklist e templates Star Schema"
```

---

### Task 11: Criar README.md

**Files:**
- Create: `README.md`

- [ ] **Step 1: Verificar se README.md já existe na raiz**

```bash
ls README.md 2>/dev/null && echo "EXISTE" || echo "NAO EXISTE"
```

Se existir, ler o conteúdo antes de sobrescrever.

- [ ] **Step 2: Criar `README.md`**

```markdown
# Sportsbook BI Analysis

Sistema de análise de dados da temporada de futebol romeno 2018/19.
Entrega respostas sobre performance, comportamento de clientes e preferências de apostas
— não apenas dashboards.

## O que o sistema entrega

- **Pipeline de dados** — CSV → bronze → silver (star schema) → gold usando PostgreSQL + Docker
- **Dashboard interativo** — análise exploratória da temporada por segmento, CRM level,
  canal e período (Streamlit + Plotly)
- **Agente de BI** — responde perguntas de negócio sobre a temporada em linguagem natural
  (Agno + Claude)

## Arquitetura

```
data/raw/*.csv
      │
      ▼
┌─────────────┐
│   BRONZE    │  src/ingestion/
│ (PostgreSQL)│  Ingestão direta dos CSVs, sem transformação
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   SILVER    │  src/transformation/silver/
│ (Star Schema│  Limpeza, tipagem, Star Schema (fato + dimensão)
│  PostgreSQL)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    GOLD     │  src/transformation/gold/
│ (PostgreSQL)│  Métricas agregadas por cliente, segmento e CRM level
└──────┬──────┘
       │
       ├──────────────────────┐
       ▼                      ▼
┌─────────────┐      ┌──────────────────┐
│  DASHBOARD  │      │     AGENTE       │
│  Streamlit  │      │  Agno + Claude   │
│  :8501      │      │  (aba no painel) │
└─────────────┘      └──────────────────┘
```

## As perguntas de negócio que o sistema responde

**P1 — Como foi a performance geral da temporada?**
Gross Revenue, Turnover e Margem mês a mês. Evolução da base de clientes ativos.

**P2 — Como se comportou a base de clientes?**
Segmentação em novos, existentes e saindo. Volume e receita por segmento ao longo da temporada.

**P3 — Quais são as preferências dos apostadores?**
Live vs. Pre-event, canal preferido (Android/iOS/Web), mercados mais apostados
e horários de pico de atividade.

**P4 — Como performa cada CRM Level?**
Gross Revenue, Turnover e número de apostas por nível. Quais níveis geram mais valor.

**P5 — Como foi a adoção do Cash Out?**
Taxa de adoção, taxa de sucesso e valor médio por tentativa. Evolução mês a mês
(funcionalidade nova na temporada).

Use o agente para fazer estas perguntas diretamente em linguagem natural.

## Como rodar

### Docker (recomendado)

Pré-requisito: Docker Desktop instalado e `ANTHROPIC_API_KEY` disponível.

```bash
# Clone o repositório
git clone https://github.com/jurandircln/sportsbook-bi-analysis.git
cd sportsbook-bi-analysis

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com sua ANTHROPIC_API_KEY

# Copie os CSVs para data/raw/
# (Cashouts.csv, Customer.csv, Customer_crm_level.csv, Events.csv, Sportsbook.csv)

# Suba o ambiente
docker compose up -d
```

Dashboard disponível em: **http://localhost:8501**

### Local (uv)

Pré-requisito: uv instalado e Python 3.12+.

```bash
git clone https://github.com/jurandircln/sportsbook-bi-analysis.git
cd sportsbook-bi-analysis

uv sync
cp .env.example .env   # edite com sua ANTHROPIC_API_KEY

# Suba o PostgreSQL
docker compose up postgres -d

# Execute o pipeline
uv run python src/ingestion/run_ingestion.py
uv run python src/transformation/run_silver.py
uv run python src/transformation/run_gold.py

# Suba o dashboard
uv run streamlit run src/dashboard/app.py
```

## Variáveis de ambiente

| Variável | Obrigatório | Descrição |
|---|---|---|
| ANTHROPIC_API_KEY | Sim | Chave da API Anthropic para o agente de IA |
| POSTGRES_USER | Sim | Usuário do PostgreSQL |
| POSTGRES_PASSWORD | Sim | Senha do PostgreSQL |
| POSTGRES_DB | Sim | Nome do banco de dados |
| DATABASE_URL | Sim | URL de conexão completa |

Ver `.env.example` para valores padrão.

## Estrutura do projeto

```
sportsbook-bi-analysis/
├── CLAUDE.md                    # Guia de desenvolvimento com IA (SDD)
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml               # Dependências (uv)
├── data/
│   └── raw/                     # CSVs originais — não versionados
├── sql/
│   ├── bronze/                  # DDLs da camada Bronze
│   ├── silver/                  # DDLs Star Schema (fact_* + dim_*)
│   └── gold/                    # DDLs das métricas analíticas
├── src/
│   ├── ingestion/               # CSV → Bronze
│   ├── transformation/          # Bronze → Silver → Gold
│   ├── agent/                   # Agente Agno + SQL tools
│   └── dashboard/               # Aplicação Streamlit
├── docs/
│   ├── business-context/        # Visão, personas, jornadas, KPIs
│   ├── product-context/         # Regras de negócio, glossário
│   └── technical-context/       # Stack, ADRs, catálogo de dados
└── tests/
```

## Stack

| Tecnologia | Versão | Papel |
|---|---|---|
| Python | 3.12+ | Runtime |
| PostgreSQL | 16 | Banco de dados (schemas bronze/silver/gold) |
| Docker + Compose | latest | Ambiente reproduzível |
| Streamlit | ≥1.32 | Dashboard interativo |
| Plotly | ≥5.20 | Visualizações |
| Agno | ≥1.4 | Framework de agentes de IA |
| Claude (Anthropic) | claude-sonnet-4-6 | LLM do agente |
| uv | latest | Gerenciamento de dependências |
```

- [ ] **Step 3: Verificar o arquivo criado**

```bash
wc -l README.md
```

Esperado: mais de 100 linhas.

```bash
grep -c "^#" README.md
```

Esperado: pelo menos 6 seções de cabeçalho.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: criar README.md com arquitetura, perguntas de negócio e instruções de uso"
```

---

### Task 12: Push final para o GitHub

**Files:** nenhum (apenas git push)

- [ ] **Step 1: Verificar status do repositório**

```bash
git status
git log --oneline -12
```

Esperado: working tree limpa; 10+ commits novos desde o último push.

- [ ] **Step 2: Verificar que todos os arquivos esperados existem**

```bash
ls sql/silver/
```

Esperado: 9 arquivos (001 ao 009).

```bash
ls docs/technical-context/adr/ | grep ADR-006
```

Esperado: `ADR-006-star-schema-silver.md`

```bash
ls README.md
```

Esperado: arquivo presente.

- [ ] **Step 3: Push para o GitHub**

```bash
git push origin main
```

Esperado: `Branch 'main' set up to track remote branch 'main' from 'origin'.` ou `Everything up-to-date` após os commits.

- [ ] **Step 4: Confirmar no GitHub**

```bash
git log origin/main --oneline -5
```

Esperado: commits do Star Schema visíveis no remoto.
