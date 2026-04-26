# Design: Pipeline de Dados — Bronze → Silver → Gold

**Data:** 2026-04-26
**Status:** Aprovado
**Repositório:** https://github.com/jurandircln/sportsbook-bi-analysis

---

## 1. Contexto e Motivação

Os 5 CSVs da temporada de futebol romeno 2018/19 estão disponíveis em `data/raw/`.
O banco já tem os schemas e tabelas criados via `docker/init.sql`.
Esta spec define o pipeline que popula as três camadas: Bronze (dados brutos), Silver
(Star Schema tipado com regras de negócio) e Gold (métricas analíticas prontas para consumo).

**Escopo:**
- `src/db.py` — factory do engine SQLAlchemy
- `src/ingestion/loader.py` + `run_ingestion.py` — CSV → Bronze
- `src/transformation/silver.py` + `run_silver.py` — Bronze → Silver
- `src/transformation/gold.py` + `run_gold.py` — Silver → Gold
- `tests/` — testes de integração com fixtures

---

## 2. Arquitetura

```
data/raw/*.csv
      │  pandas.read_csv()
      ▼
bronze.*           ← loader.py (truncate + to_sql, todos os tipos TEXT)
      │  SQL INSERT ... SELECT + pandas (dim_crm_level)
      ▼
silver.*           ← silver.py (Star Schema, regras de negócio aplicadas)
      │  SQL INSERT ... SELECT
      ▼
gold.*             ← gold.py (agregações analíticas)
```

**Estratégia:** truncate-and-reload em cada execução. Para dados históricos fixos,
elimina necessidade de lógica de upsert e risco de duplicatas.

**Entry points:**
```bash
uv run python src/ingestion/run_ingestion.py
uv run python src/transformation/run_silver.py
uv run python src/transformation/run_gold.py
```

---

## 3. Estrutura de Arquivos

```
src/
├── db.py                        # get_engine() — lê DATABASE_URL do .env
├── ingestion/
│   ├── __init__.py
│   ├── loader.py                # load_all_csvs_to_bronze(engine, data_dir)
│   └── run_ingestion.py         # entry point
├── transformation/
│   ├── __init__.py
│   ├── silver.py                # populate_silver(engine) — 8 tabelas
│   ├── gold.py                  # populate_gold(engine) — 6 tabelas
│   ├── run_silver.py            # entry point
│   └── run_gold.py              # entry point
tests/
├── fixtures/
│   ├── Customer.csv             # ~15 linhas
│   ├── Customer_crm_level.csv
│   ├── Events.csv
│   ├── Sportsbook.csv
│   └── Cashouts.csv
├── conftest.py                  # engine fixture + DDL setup/teardown
├── test_ingestion.py
├── test_silver.py
└── test_gold.py
```

---

## 4. src/db.py

Responsabilidade única: criar e retornar o SQLAlchemy engine.

```python
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

def get_engine():
    load_dotenv()
    url = os.environ["DATABASE_URL"]
    return create_engine(url)
```

---

## 5. Bronze: Ingestão CSV → Bronze

**Arquivo:** `src/ingestion/loader.py`

Uma função por tabela + orquestradora. Cada função:
1. `pd.read_csv(path, dtype=str)` — força todos os tipos como string
2. Renomeia colunas para os nomes das colunas Bronze (snake_case)
3. `TRUNCATE bronze.<tabela>` via `conn.execute(text(...))`
4. `df.to_sql(schema='bronze', if_exists='append', index=False)`

**Mapeamento de colunas:**

| CSV | Bronze |
|---|---|
| `Customer_ID` | `customer_id` |
| `Customer_DateCreation_ID` | `customer_datecreation_id` |
| `Customer_Gender_Name` | `customer_gender_name` |
| `Customer_Birthday` | `customer_birthday` |
| `Date_YearMonth` | `date_yearmonth` |
| `CRM_Level` | `crm_level` |
| `Event_ID` | `event_id` |
| `Event_Sport_Name` | `event_sport_name` |
| `Event_Class_Name` | `event_class_name` |
| `Event_Type_Name` | `event_type_name` |
| `Event_Name` | `event_name` |
| `Event_Start_Time` | `event_start_time` |
| `Event_End_Time` | `event_end_time` |
| `SportBetSettled_Bet_ID` | `sportbetsettled_bet_id` |
| `BetType_Name` | `bettype_name` |
| `Market_Template_Name` | `market_template_name` |
| `SportBetSettled_Customer_ID` | `sportbetsettled_customer_id` |
| `SportBetSettled_Settled` | `sportbetsettled_settled` |
| `SportBetSettled_Placed` | `sportbetsettled_placed` |
| `Channel_Name` | `channel_name` |
| `SportBetSettled_Event_ID` | `sportbetsettled_event_id` |
| `Turnover` | `turnover` |
| `Winnings` | `winnings` |
| `CashoutAttempt_Bet_ID` | `cashout_attempt_bet_id` |
| `CashoutAttempt_Bet_CashOut_ID` | `cashout_attempt_bet_cashout_id` |
| `CashoutAttempt_Bet_CashOut_Created` | `cashout_attempt_bet_cashout_created` |
| `CashoutAttempt_Bet_CashOut_Status` | `cashout_attempt_bet_cashout_status` |
| `CashoutAttempt_CashOut_Amount` | `cashout_attempt_cashout_amount` |

**Saída:** log com contagem de linhas por tabela, ex:
```
bronze.customer        → 10.234 linhas
bronze.customer_crm_level → 8.421 linhas
bronze.events          → 2.187 linhas
bronze.sportsbook      → 523.891 linhas
bronze.cashouts        → 15.672 linhas
```

---

## 6. Silver: Transformações Bronze → Silver

**Arquivo:** `src/transformation/silver.py`

Orquestradora: `populate_silver(engine)` — chama cada função na ordem correta
(dimensões antes dos fatos; `dim_crm_level` após `dim_customer`).

### 6.1 dim_customer (SQL)

```sql
TRUNCATE silver.dim_customer;
INSERT INTO silver.dim_customer
    (customer_id, registration_date, gender, birth_date, age, ingested_at)
SELECT
    customer_id::INTEGER,
    customer_datecreation_id::DATE,
    NULLIF(customer_gender_name, ''),
    NULLIF(customer_birthday, '')::DATE,
    EXTRACT(YEAR FROM AGE(NOW(), NULLIF(customer_birthday, '')::DATE))::INTEGER,
    NOW()
FROM bronze.customer
WHERE customer_id ~ '^[0-9]+$';
```

### 6.2 dim_crm_level (Python/pandas — forward-fill)

RN-003: meses sem registro usam o nível mais recente atribuído.

```python
def _populate_dim_crm_level(engine):
    df = pd.read_sql("SELECT customer_id, date_yearmonth, crm_level FROM bronze.customer_crm_level", engine)
    df['customer_id'] = df['customer_id'].astype(int)
    df['year_month'] = pd.to_datetime(df['date_yearmonth'])

    season_end = pd.Timestamp('2019-08-01')
    rows = []
    for cid, group in df.groupby('customer_id'):
        group = group.sort_values('year_month').set_index('year_month')['crm_level']
        idx = pd.date_range(group.index.min(), season_end, freq='MS')
        filled = group.reindex(idx).ffill()
        for month, level in filled.items():
            if pd.notna(level):
                rows.append({'customer_id': cid, 'year_month': month.date(), 'crm_level': level})

    result = pd.DataFrame(rows)
    result['ingested_at'] = pd.Timestamp.now()
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE silver.dim_crm_level"))
    result.to_sql('dim_crm_level', engine, schema='silver', if_exists='append', index=False)
```

### 6.3 dim_event (SQL)

```sql
TRUNCATE silver.dim_event;
INSERT INTO silver.dim_event
    (event_id, sport_name, class_name, type_name, event_name, start_time, end_time, ingested_at)
SELECT
    event_id::INTEGER,
    NULLIF(event_sport_name, ''),
    NULLIF(event_class_name, ''),
    NULLIF(event_type_name, ''),
    NULLIF(event_name, ''),
    NULLIF(event_start_time, '')::TIMESTAMP,
    NULLIF(event_end_time, '')::TIMESTAMP,
    NOW()
FROM bronze.events
WHERE event_id ~ '^[0-9]+$';
```

### 6.4 dim_market (SQL — surrogate key)

```sql
TRUNCATE silver.dim_market RESTART IDENTITY;
INSERT INTO silver.dim_market (market_name, bet_type, ingested_at)
SELECT DISTINCT
    market_template_name,
    NULLIF(bettype_name, ''),
    NOW()
FROM bronze.sportsbook
WHERE market_template_name IS NOT NULL AND market_template_name <> '';
```

### 6.5 dim_channel (SQL — surrogate key)

```sql
TRUNCATE silver.dim_channel RESTART IDENTITY;
INSERT INTO silver.dim_channel (channel_name, ingested_at)
SELECT DISTINCT channel_name, NOW()
FROM bronze.sportsbook
WHERE channel_name IS NOT NULL AND channel_name <> '';
```

### 6.6 dim_date (SQL — gerada por generate_series)

```sql
TRUNCATE silver.dim_date;
INSERT INTO silver.dim_date
    (date_id, full_date, year, month, month_name, day, day_of_week, day_name, is_weekend, ingested_at)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INTEGER,
    d::DATE,
    EXTRACT(YEAR FROM d)::INTEGER,
    EXTRACT(MONTH FROM d)::INTEGER,
    TO_CHAR(d, 'TMMonth'),
    EXTRACT(DAY FROM d)::INTEGER,
    EXTRACT(ISODOW FROM d)::INTEGER,
    TO_CHAR(d, 'TMDay'),
    EXTRACT(ISODOW FROM d) IN (6, 7),
    NOW()
FROM generate_series('2017-07-01'::DATE, '2019-09-30'::DATE, '1 day'::INTERVAL) d;
```

> `TO_CHAR` com prefixo `TM` retorna nomes de mês/dia no locale do servidor.
> Para garantir português, o locale do PostgreSQL será configurado para `pt_BR.UTF-8`
> no docker-compose.yml. Alternativa: mapear meses manualmente em Python se o locale
> não estiver disponível no container.

### 6.7 fact_bets (SQL)

```sql
TRUNCATE silver.fact_bets;
INSERT INTO silver.fact_bets
    (bet_id, customer_id, event_id, date_id, market_id, channel_id,
     placed_at, settled_at, placed_hour, turnover, winnings, gross_revenue, is_live, ingested_at)
SELECT
    sb.sportbetsettled_bet_id,
    sb.sportbetsettled_customer_id::INTEGER,
    NULLIF(sb.sportbetsettled_event_id, '')::INTEGER,
    TO_CHAR(sb.sportbetsettled_placed::TIMESTAMP, 'YYYYMMDD')::INTEGER,
    dm.market_id,
    dc.channel_id,
    sb.sportbetsettled_placed::TIMESTAMP,
    NULLIF(sb.sportbetsettled_settled, '')::TIMESTAMP,
    EXTRACT(HOUR FROM sb.sportbetsettled_placed::TIMESTAMP)::INTEGER,
    sb.turnover::NUMERIC(12,2),
    sb.winnings::NUMERIC(12,2),
    sb.turnover::NUMERIC(12,2) - sb.winnings::NUMERIC(12,2),
    sb.sportbetsettled_placed::TIMESTAMP >= COALESCE(de.start_time, 'infinity'::TIMESTAMP),
    NOW()
FROM bronze.sportsbook sb
LEFT JOIN silver.dim_market dm
    ON dm.market_name = sb.market_template_name
    AND (dm.bet_type = NULLIF(sb.bettype_name, '') OR (dm.bet_type IS NULL AND NULLIF(sb.bettype_name, '') IS NULL))
LEFT JOIN silver.dim_channel dc
    ON dc.channel_name = sb.channel_name
LEFT JOIN silver.dim_event de
    ON de.event_id = NULLIF(sb.sportbetsettled_event_id, '')::INTEGER
WHERE sb.sportbetsettled_bet_id IS NOT NULL;
```

> `is_live = placed_at >= event_start_time` — se `event_start_time` for NULL, a aposta
> é classificada como Pre-event (COALESCE com 'infinity') — conforme RN-002.

### 6.8 fact_cashouts (SQL)

```sql
TRUNCATE silver.fact_cashouts;
INSERT INTO silver.fact_cashouts
    (cashout_id, bet_id, date_id, created_at, status, cashout_amount, ingested_at)
SELECT
    cashout_attempt_bet_cashout_id,
    cashout_attempt_bet_id,
    TO_CHAR(cashout_attempt_bet_cashout_created::TIMESTAMP, 'YYYYMMDD')::INTEGER,
    cashout_attempt_bet_cashout_created::TIMESTAMP,
    cashout_attempt_bet_cashout_status,
    NULLIF(cashout_attempt_cashout_amount, '')::NUMERIC(12,2),
    NOW()
FROM bronze.cashouts
WHERE cashout_attempt_bet_cashout_id IS NOT NULL;
```

---

## 7. Gold: Agregações Silver → Gold

**Arquivo:** `src/transformation/gold.py`

Orquestradora: `populate_gold(engine)` — chama cada função na ordem abaixo.
A temporada é `'2018-09-01'` a `'2019-08-31'` (RN-005).

### 7.1 customer_performance

```sql
TRUNCATE gold.customer_performance;
INSERT INTO gold.customer_performance
    (customer_id, gender, age, total_bets, total_turnover, total_winnings,
     gross_revenue, live_bets, pre_event_bets, cashout_attempts, successful_cashouts, updated_at)
SELECT
    dc.customer_id,
    dc.gender,
    dc.age,
    COUNT(fb.bet_id),
    COALESCE(SUM(fb.turnover), 0),
    COALESCE(SUM(fb.winnings), 0),
    COALESCE(SUM(fb.gross_revenue), 0),
    COUNT(fb.bet_id) FILTER (WHERE fb.is_live),
    COUNT(fb.bet_id) FILTER (WHERE NOT fb.is_live),
    COUNT(fc.cashout_id),
    COUNT(fc.cashout_id) FILTER (WHERE fc.status = 'Success'),
    NOW()
FROM silver.dim_customer dc
LEFT JOIN silver.fact_bets fb ON fb.customer_id = dc.customer_id
LEFT JOIN silver.fact_cashouts fc ON fc.bet_id = fb.bet_id
GROUP BY dc.customer_id, dc.gender, dc.age;
```

### 7.2 customer_segments (RN-004)

```sql
TRUNCATE gold.customer_segments;
INSERT INTO gold.customer_segments
    (customer_id, segment, first_bet_date, last_bet_date, crm_level, updated_at)
WITH activity AS (
    SELECT
        customer_id,
        MIN(placed_at::DATE)                                            AS first_bet_date,
        MAX(placed_at::DATE)                                            AS last_bet_date,
        BOOL_OR(placed_at >= '2018-09-01' AND placed_at < '2019-09-01') AS in_season,
        BOOL_OR(placed_at < '2018-09-01')                               AS pre_season,
        BOOL_OR(placed_at >= '2019-06-01' AND placed_at < '2019-09-01') AS last_3_months
    FROM silver.fact_bets
    GROUP BY customer_id
),
crm_latest AS (
    SELECT DISTINCT ON (customer_id) customer_id, crm_level
    FROM silver.dim_crm_level
    WHERE year_month <= '2019-08-01'
    ORDER BY customer_id, year_month DESC
)
SELECT
    a.customer_id,
    CASE
        WHEN a.in_season AND NOT a.pre_season         THEN 'novo'
        WHEN a.in_season AND a.pre_season             THEN 'existente'
        WHEN a.pre_season AND NOT a.last_3_months     THEN 'saindo'
        ELSE 'novo'
    END,
    a.first_bet_date,
    a.last_bet_date,
    cl.crm_level,
    NOW()
FROM activity a
LEFT JOIN crm_latest cl ON cl.customer_id = a.customer_id
WHERE a.in_season OR a.pre_season;
```

### 7.3 betting_preferences

```sql
TRUNCATE gold.betting_preferences;
INSERT INTO gold.betting_preferences
    (customer_id, preferred_channel, preferred_market, preferred_bet_type,
     live_bet_pct, peak_hour, updated_at)
SELECT
    fb.customer_id,
    MODE() WITHIN GROUP (ORDER BY dc.channel_name)  AS preferred_channel,
    MODE() WITHIN GROUP (ORDER BY dm.market_name)   AS preferred_market,
    MODE() WITHIN GROUP (ORDER BY dm.bet_type)      AS preferred_bet_type,
    ROUND(AVG(fb.is_live::INT) * 100, 2)            AS live_bet_pct,
    MODE() WITHIN GROUP (ORDER BY fb.placed_hour)   AS peak_hour,
    NOW()
FROM silver.fact_bets fb
LEFT JOIN silver.dim_channel dc ON dc.channel_id = fb.channel_id
LEFT JOIN silver.dim_market  dm ON dm.market_id  = fb.market_id
GROUP BY fb.customer_id;
```

### 7.4 crm_performance

```sql
TRUNCATE gold.crm_performance;
INSERT INTO gold.crm_performance
    (crm_level, customer_count, total_bets, total_turnover, total_winnings,
     gross_revenue, avg_bets_per_customer, avg_turnover_per_customer,
     avg_gross_revenue_per_customer, updated_at)
SELECT
    dcl.crm_level,
    COUNT(DISTINCT fb.customer_id),
    COUNT(fb.bet_id),
    SUM(fb.turnover),
    SUM(fb.winnings),
    SUM(fb.gross_revenue),
    ROUND(COUNT(fb.bet_id)::NUMERIC       / NULLIF(COUNT(DISTINCT fb.customer_id), 0), 2),
    ROUND(SUM(fb.turnover)::NUMERIC       / NULLIF(COUNT(DISTINCT fb.customer_id), 0), 2),
    ROUND(SUM(fb.gross_revenue)::NUMERIC  / NULLIF(COUNT(DISTINCT fb.customer_id), 0), 2),
    NOW()
FROM silver.fact_bets fb
JOIN silver.dim_crm_level dcl
    ON dcl.customer_id = fb.customer_id
    AND dcl.year_month = DATE_TRUNC('month', fb.placed_at)::DATE
GROUP BY dcl.crm_level;
```

### 7.5 season_summary

```sql
TRUNCATE gold.season_summary;
INSERT INTO gold.season_summary
    (month, total_customers, new_customers, churned_customers, total_bets,
     total_turnover, total_winnings, gross_revenue, live_bet_pct, updated_at)
SELECT
    DATE_TRUNC('month', fb.placed_at)::DATE,
    COUNT(DISTINCT fb.customer_id),
    COUNT(DISTINCT fb.customer_id) FILTER (
        WHERE NOT EXISTS (
            SELECT 1 FROM silver.fact_bets fb2
            WHERE fb2.customer_id = fb.customer_id
              AND fb2.placed_at < DATE_TRUNC('month', fb.placed_at)
        )
    ),
    0,   -- churned calculado em pós-processamento ou deixado para o agente
    COUNT(fb.bet_id),
    SUM(fb.turnover),
    SUM(fb.winnings),
    SUM(fb.gross_revenue),
    ROUND(AVG(fb.is_live::INT) * 100, 2),
    NOW()
FROM silver.fact_bets fb
WHERE fb.placed_at >= '2018-09-01' AND fb.placed_at < '2019-09-01'
GROUP BY DATE_TRUNC('month', fb.placed_at)::DATE
ORDER BY 1;
```

### 7.6 cashout_analysis

```sql
TRUNCATE gold.cashout_analysis;
INSERT INTO gold.cashout_analysis
    (month, total_attempts, successful_attempts, failed_attempts,
     success_rate, total_cashout_amount, avg_cashout_amount, updated_at)
SELECT
    DATE_TRUNC('month', fc.created_at)::DATE,
    COUNT(*),
    COUNT(*) FILTER (WHERE fc.status = 'Success'),
    COUNT(*) FILTER (WHERE fc.status <> 'Success'),
    ROUND(AVG((fc.status = 'Success')::INT) * 100, 2),
    COALESCE(SUM(fc.cashout_amount), 0),
    COALESCE(ROUND(AVG(fc.cashout_amount), 2), 0),
    NOW()
FROM silver.fact_cashouts fc
WHERE fc.created_at >= '2018-09-01' AND fc.created_at < '2019-09-01'
GROUP BY DATE_TRUNC('month', fc.created_at)::DATE
ORDER BY 1;
```

---

## 8. Testes de Integração

**Fixtures:** subsets dos CSVs com ~15 linhas cobrindo:
- Clientes com e sem data de nascimento
- Clientes com múltiplos registros CRM e gap entre eles (forward-fill verificável)
- Apostas live e pre-event (para testar `is_live`)
- Cashouts Success e Failed
- Pelo menos 3 meses de atividade para testar `season_summary`

**`tests/conftest.py`:**
- Fixture `engine` com scope `session`: cria engine apontando para banco de testes
- Fixture `loaded_bronze`: chama `load_all_csvs_to_bronze` com o diretório `tests/fixtures/`
- Fixture `loaded_silver`: depende de `loaded_bronze`, chama `populate_silver`
- Fixture `loaded_gold`: depende de `loaded_silver`, chama `populate_gold`

**`tests/test_ingestion.py`:**
- Contagem de linhas em cada tabela Bronze bate com o CSV fixture
- Todas as colunas Bronze são TEXT (nenhuma conversão de tipo)

**`tests/test_silver.py`:**
- `dim_customer`: `age` correto para pelo menos 1 cliente com birth_date conhecida
- `dim_crm_level`: cliente com gap entre registros tem o mês intermediário preenchido com o nível anterior
- `fact_bets`: `gross_revenue = turnover - winnings` para todas as linhas
- `fact_bets`: aposta com `placed_at >= event_start_time` tem `is_live = TRUE`
- `fact_bets`: aposta com `placed_at < event_start_time` tem `is_live = FALSE`
- `fact_cashouts`: `date_id = TO_CHAR(created_at, 'YYYYMMDD')::INTEGER`

**`tests/test_gold.py`:**
- `customer_segments`: cliente com aposta somente dentro da temporada → `novo`
- `customer_segments`: cliente com aposta antes e durante → `existente`
- `season_summary`: soma de `gross_revenue` bate com `SUM(silver.fact_bets.gross_revenue)` para o mesmo período

---

## 9. Considerações de Locale (dim_date)

`TO_CHAR(d, 'TMMonth')` retorna o nome do mês no locale do servidor PostgreSQL.
Para garantir nomes em português, adicionar ao `docker-compose.yml`:

```yaml
environment:
  POSTGRES_INITDB_ARGS: "--locale=pt_BR.UTF-8"
```

Se o locale `pt_BR.UTF-8` não estiver disponível no container `postgres:16-alpine`,
usar um mapeamento estático em Python (dicionário `{1: 'Janeiro', ..., 12: 'Dezembro'}`).
O plano de implementação definirá qual abordagem usar após verificação.

---

## 10. Resumo dos Artefatos

| Artefato | Ação |
|---|---|
| `src/db.py` | Criar |
| `src/ingestion/loader.py` | Criar |
| `src/ingestion/run_ingestion.py` | Criar |
| `src/transformation/silver.py` | Criar |
| `src/transformation/run_silver.py` | Criar |
| `src/transformation/gold.py` | Criar |
| `src/transformation/run_gold.py` | Criar |
| `tests/conftest.py` | Criar |
| `tests/test_ingestion.py` | Criar |
| `tests/test_silver.py` | Criar |
| `tests/test_gold.py` | Criar |
| `tests/fixtures/*.csv` | Criar |
| `docker-compose.yml` | Atualizar (locale pt_BR) |
