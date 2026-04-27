# Pipeline de Dados — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar o pipeline completo de dados: CSV → Bronze → Silver (Star Schema) → Gold, com testes de integração cobrindo todas as regras de negócio.

**Architecture:** Pandas lê os CSVs e popula o Bronze (truncate + append). Silver usa SQL `INSERT … SELECT` para 6 das 8 tabelas; `dim_crm_level` e `dim_date` usam pandas (forward-fill e geração de calendário). Gold usa SQL puro com CTEs e agregações. Cada camada tem entry point próprio (`run_ingestion.py`, `run_silver.py`, `run_gold.py`).

**Tech Stack:** Python 3.12, pandas, SQLAlchemy 2, psycopg2-binary, python-dotenv, pytest, PostgreSQL 16.

**Spec:** `docs/superpowers/specs/2026-04-26-pipeline-dados-design.md`

---

## Mapa de Arquivos

| Ação | Arquivo |
|---|---|
| Criar | `src/db.py` |
| Criar | `src/ingestion/loader.py` |
| Criar | `src/ingestion/run_ingestion.py` |
| Criar | `src/transformation/silver.py` |
| Criar | `src/transformation/run_silver.py` |
| Criar | `src/transformation/gold.py` |
| Criar | `src/transformation/run_gold.py` |
| Criar | `tests/conftest.py` |
| Criar | `tests/fixtures/Customer.csv` |
| Criar | `tests/fixtures/Customer_crm_level.csv` |
| Criar | `tests/fixtures/Events.csv` |
| Criar | `tests/fixtures/Sportsbook.csv` |
| Criar | `tests/fixtures/Cashouts.csv` |
| Criar | `tests/test_ingestion.py` |
| Criar | `tests/test_silver.py` |
| Criar | `tests/test_gold.py` |

---

## Formatos de Dados Reais (verificados nos CSVs)

| Campo | Formato | Exemplo |
|---|---|---|
| `Customer_DateCreation_ID` | `YYYYMMDD` | `20170625` |
| `Customer_Birthday` | ISO 8601 com Z | `1997-07-25T00:00:00.000Z` |
| `Date_YearMonth` (CRM) | `YYYYMM` | `201902` |
| Timestamps (Events, Sportsbook, Cashouts) | ISO 8601 com Z | `2018-10-20T16:01:36.000Z` |
| Cashout status | string | `Successful` / `Failed` |
| CRM customer column | `NEW_Customer_ID` | — |

---

### Task 1: src/db.py e tests/conftest.py

**Files:**
- Create: `src/db.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Criar `src/db.py`**

```python
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


def get_engine():
    load_dotenv()
    url = os.environ["DATABASE_URL"]
    return create_engine(url)
```

- [ ] **Step 2: Criar `tests/conftest.py`**

```python
import pytest
from pathlib import Path
from src.db import get_engine
from src.ingestion.loader import load_all_csvs_to_bronze
from src.transformation.silver import populate_silver
from src.transformation.gold import populate_gold

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def engine():
    return get_engine()


@pytest.fixture(scope="session")
def loaded_bronze(engine):
    load_all_csvs_to_bronze(engine, FIXTURES_DIR)
    return engine


@pytest.fixture(scope="session")
def loaded_silver(loaded_bronze):
    populate_silver(loaded_bronze)
    return loaded_bronze


@pytest.fixture(scope="session")
def loaded_gold(loaded_silver):
    populate_gold(loaded_silver)
    return loaded_silver
```

- [ ] **Step 3: Verificar que os módulos existem**

```bash
ls src/ingestion/ src/transformation/
```

Esperado: `__init__.py` em cada diretório.

- [ ] **Step 4: Commit**

```bash
git add src/db.py tests/conftest.py
git commit -m "feat: adicionar db.py e conftest.py base"
```

---

### Task 2: Criar fixtures CSV para testes

**Files:**
- Create: `tests/fixtures/Customer.csv`
- Create: `tests/fixtures/Customer_crm_level.csv`
- Create: `tests/fixtures/Events.csv`
- Create: `tests/fixtures/Sportsbook.csv`
- Create: `tests/fixtures/Cashouts.csv`

Os fixtures cobrem: clientes com e sem birthday, gaps de CRM para testar forward-fill, apostas live e pre-event, cashouts Successful e Failed, clientes com segmentos novo/existente/saindo.

- [ ] **Step 1: Criar `tests/fixtures/Customer.csv`**

```
Customer_ID,Customer_DateCreation_ID,Customer_Gender_Name,Customer_Birthday
1,20150315,Male,1985-06-20T00:00:00.000Z
2,20181001,Female,1992-03-10T00:00:00.000Z
3,20170520,Male,
4,20160830,Female,1978-11-05T00:00:00.000Z
5,20180915,Male,1995-07-25T00:00:00.000Z
```

- [ ] **Step 2: Criar `tests/fixtures/Customer_crm_level.csv`**

```
NEW_Customer_ID,Date_YearMonth,CRM_Level
1,201809,Bronze
1,201901,Silver
2,201811,Gold
3,201809,Bronze
```

> Cliente 1 tem gap Out-Dez/2018 — deve ser preenchido com Bronze no forward-fill.

- [ ] **Step 3: Criar `tests/fixtures/Events.csv`**

```
Event_ID,Event_Sport_Name,Event_Class_Name,Event_Type_Name,Event_Name,Event_Start_Time,Event_End_Time
101,Football,Romanian,Liga 1,CFR Cluj vs FCSB,2018-09-15T18:00:00.000Z,2018-09-15T20:00:00.000Z
102,Football,Romanian,Liga 1,Dinamo vs Rapid,2018-10-20T15:00:00.000Z,2018-10-20T17:00:00.000Z
103,Football,Romanian,Liga 1,Viitorul vs Craiova,2019-03-10T20:00:00.000Z,2019-03-10T22:00:00.000Z
```

- [ ] **Step 4: Criar `tests/fixtures/Sportsbook.csv`**

```
SportBetSettled_Bet_ID,BetType_Name,Market_Template_Name,SportBetSettled_Customer_ID,SportBetSettled_Settled,SportBetSettled_Placed,Channel_Name,SportBetSettled_Event_ID,Turnover,Winnings
BET001,Single,Match Winner,1,2018-09-15T21:00:00.000Z,2018-09-15T17:30:00.000Z,Android,101,10.00,0.00
BET002,Single,Match Winner,1,2018-09-15T21:00:00.000Z,2018-09-15T19:00:00.000Z,Android,101,5.00,15.00
BET003,Single,Both Teams Score,2,2018-10-20T17:30:00.000Z,2018-10-20T14:00:00.000Z,iOS,102,20.00,0.00
BET004,Accumulator,Match Winner,3,2019-03-10T22:30:00.000Z,2019-03-10T21:00:00.000Z,Web,103,15.00,30.00
BET005,Single,Match Winner,4,2018-09-30T21:00:00.000Z,2018-09-10T10:00:00.000Z,Android,101,8.00,0.00
BET006,Single,Over/Under,5,2019-06-20T21:00:00.000Z,2019-06-20T10:00:00.000Z,iOS,,12.00,20.00
BET007,Single,Match Winner,1,2018-04-15T21:00:00.000Z,2018-04-10T10:00:00.000Z,Android,,5.00,0.00
BET008,Single,Match Winner,4,2018-07-20T21:00:00.000Z,2018-07-15T10:00:00.000Z,iOS,,8.00,0.00
```

> BET001 placed=17:30, event starts=18:00 → pre-event. BET002 placed=19:00 → live.
> BET007/BET008 são pré-temporada (Apr/Jul 2018) para testar segmentos existente/saindo.
> BET006 sem event_id → is_live=FALSE (COALESCE com infinity).

- [ ] **Step 5: Criar `tests/fixtures/Cashouts.csv`**

```
CashoutAttempt_Bet_ID,CashoutAttempt_Bet_Cashout_ID,CashoutAttempt_Bet_Cashout_Created,CashoutAttempt_Bet_Cashout_Status,CashoutAttempt_Cashout_Amount
BET003,CO001,2018-10-20T16:00:00.000Z,Successful,12.50
BET001,CO002,2018-09-15T20:00:00.000Z,Failed,
BET005,CO003,2018-09-25T15:00:00.000Z,Successful,6.00
```

- [ ] **Step 6: Verificar fixtures**

```bash
ls tests/fixtures/
wc -l tests/fixtures/*.csv
```

Esperado: 5 arquivos, Customer.csv=6 linhas, Events.csv=4, Sportsbook.csv=9, Cashouts.csv=4, Customer_crm_level.csv=5.

- [ ] **Step 7: Commit**

```bash
git add tests/fixtures/
git commit -m "test: adicionar fixtures CSV para testes de integração"
```

---

### Task 3: src/ingestion/loader.py (TDD)

**Files:**
- Create: `tests/test_ingestion.py`
- Create: `src/ingestion/loader.py`

- [ ] **Step 1: Escrever teste falhando**

```python
# tests/test_ingestion.py
from sqlalchemy import text


def test_bronze_customer_row_count(loaded_bronze):
    with loaded_bronze.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM bronze.customer")).scalar()
    assert count == 5


def test_bronze_sportsbook_row_count(loaded_bronze):
    with loaded_bronze.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM bronze.sportsbook")).scalar()
    assert count == 8


def test_bronze_customer_all_text(loaded_bronze):
    with loaded_bronze.connect() as conn:
        row = conn.execute(text(
            "SELECT customer_id, customer_datecreation_id FROM bronze.customer LIMIT 1"
        )).fetchone()
    assert isinstance(row[0], str)
    assert isinstance(row[1], str)


def test_bronze_crm_customer_id_column(loaded_bronze):
    with loaded_bronze.connect() as conn:
        row = conn.execute(text(
            "SELECT customer_id FROM bronze.customer_crm_level LIMIT 1"
        )).fetchone()
    assert row is not None
```

- [ ] **Step 2: Rodar teste para ver falhar**

```bash
uv run pytest tests/test_ingestion.py -v
```

Esperado: FAIL — `ImportError: cannot import name 'load_all_csvs_to_bronze' from 'src.ingestion.loader'`

- [ ] **Step 3: Implementar `src/ingestion/loader.py`**

```python
import pandas as pd
from pathlib import Path
from sqlalchemy import text

_CUSTOMER_RENAME = {
    'Customer_ID': 'customer_id',
    'Customer_DateCreation_ID': 'customer_datecreation_id',
    'Customer_Gender_Name': 'customer_gender_name',
    'Customer_Birthday': 'customer_birthday',
}

_CRM_RENAME = {
    'NEW_Customer_ID': 'customer_id',
    'Date_YearMonth': 'date_yearmonth',
    'CRM_Level': 'crm_level',
}

_EVENTS_RENAME = {
    'Event_ID': 'event_id',
    'Event_Sport_Name': 'event_sport_name',
    'Event_Class_Name': 'event_class_name',
    'Event_Type_Name': 'event_type_name',
    'Event_Name': 'event_name',
    'Event_Start_Time': 'event_start_time',
    'Event_End_Time': 'event_end_time',
}

_SPORTSBOOK_RENAME = {
    'SportBetSettled_Bet_ID': 'sportbetsettled_bet_id',
    'BetType_Name': 'bettype_name',
    'Market_Template_Name': 'market_template_name',
    'SportBetSettled_Customer_ID': 'sportbetsettled_customer_id',
    'SportBetSettled_Settled': 'sportbetsettled_settled',
    'SportBetSettled_Placed': 'sportbetsettled_placed',
    'Channel_Name': 'channel_name',
    'SportBetSettled_Event_ID': 'sportbetsettled_event_id',
    'Turnover': 'turnover',
    'Winnings': 'winnings',
}

_CASHOUTS_RENAME = {
    'CashoutAttempt_Bet_ID': 'cashout_attempt_bet_id',
    'CashoutAttempt_Bet_Cashout_ID': 'cashout_attempt_bet_cashout_id',
    'CashoutAttempt_Bet_Cashout_Created': 'cashout_attempt_bet_cashout_created',
    'CashoutAttempt_Bet_Cashout_Status': 'cashout_attempt_bet_cashout_status',
    'CashoutAttempt_Cashout_Amount': 'cashout_attempt_cashout_amount',
}


def _load(engine, path: Path, table: str, rename: dict) -> int:
    df = pd.read_csv(path, dtype=str).rename(columns=rename)
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE bronze.{table}"))
    df.to_sql(table, engine, schema='bronze', if_exists='append', index=False)
    return len(df)


def load_all_csvs_to_bronze(engine, data_dir: Path) -> None:
    data_dir = Path(data_dir)
    counts = {
        'customer':          _load(engine, data_dir / 'Customer.csv',            'customer',          _CUSTOMER_RENAME),
        'customer_crm_level':_load(engine, data_dir / 'Customer_crm_level.csv',  'customer_crm_level',_CRM_RENAME),
        'events':            _load(engine, data_dir / 'Events.csv',               'events',            _EVENTS_RENAME),
        'sportsbook':        _load(engine, data_dir / 'Sportsbook.csv',           'sportsbook',        _SPORTSBOOK_RENAME),
        'cashouts':          _load(engine, data_dir / 'Cashouts.csv',             'cashouts',          _CASHOUTS_RENAME),
    }
    for table, n in counts.items():
        print(f"bronze.{table:25s} → {n:>8,} linhas")
```

- [ ] **Step 4: Rodar testes**

```bash
uv run pytest tests/test_ingestion.py -v
```

Esperado: 4 testes PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/ingestion/loader.py tests/test_ingestion.py
git commit -m "feat: implementar Bronze ingestion CSV→PostgreSQL (TDD)"
```

---

### Task 4: src/ingestion/run_ingestion.py

**Files:**
- Create: `src/ingestion/run_ingestion.py`

- [ ] **Step 1: Criar entry point**

```python
from pathlib import Path
from src.db import get_engine
from src.ingestion.loader import load_all_csvs_to_bronze

if __name__ == "__main__":
    engine = get_engine()
    data_dir = Path(__file__).parent.parent.parent / "data" / "raw"
    print("Iniciando ingestão Bronze...")
    load_all_csvs_to_bronze(engine, data_dir)
    print("Ingestão concluída.")
```

- [ ] **Step 2: Verificar que o script roda sem erros (com Docker up)**

```bash
docker compose up -d postgres
sleep 3
uv run python src/ingestion/run_ingestion.py
```

Esperado:
```
Iniciando ingestão Bronze...
bronze.customer                   →   45,817 linhas
bronze.customer_crm_level         →   72,196 linhas
bronze.events                     →    2,645 linhas
bronze.sportsbook                 →1,499,459 linhas
bronze.cashouts                   →  137,602 linhas
Ingestão concluída.
```

(Contagens aproximadas — o que importa é não ter erros.)

- [ ] **Step 3: Commit**

```bash
git add src/ingestion/run_ingestion.py
git commit -m "feat: adicionar run_ingestion.py entry point"
```

---

### Task 5: Silver — dim_customer e dim_event (TDD)

**Files:**
- Create: `tests/test_silver.py` (parcial)
- Create: `src/transformation/silver.py` (parcial — só dim_customer e dim_event)

- [ ] **Step 1: Escrever testes para dim_customer e dim_event**

```python
# tests/test_silver.py
from decimal import Decimal
from sqlalchemy import text


def test_dim_customer_row_count(loaded_silver):
    with loaded_silver.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM silver.dim_customer")).scalar()
    assert count == 5


def test_dim_customer_id_is_integer(loaded_silver):
    with loaded_silver.connect() as conn:
        row = conn.execute(text(
            "SELECT customer_id FROM silver.dim_customer WHERE customer_id = 1"
        )).fetchone()
    assert row is not None
    assert row[0] == 1


def test_dim_customer_registration_date_is_date(loaded_silver):
    from datetime import date
    with loaded_silver.connect() as conn:
        row = conn.execute(text(
            "SELECT registration_date FROM silver.dim_customer WHERE customer_id = 1"
        )).fetchone()
    assert row[0] == date(2015, 3, 15)


def test_dim_customer_age_calculated(loaded_silver):
    with loaded_silver.connect() as conn:
        row = conn.execute(text(
            "SELECT age FROM silver.dim_customer WHERE customer_id = 1"
        )).fetchone()
    assert row[0] is not None
    assert row[0] > 0


def test_dim_customer_no_birthday_null_age(loaded_silver):
    with loaded_silver.connect() as conn:
        row = conn.execute(text(
            "SELECT age, birth_date FROM silver.dim_customer WHERE customer_id = 3"
        )).fetchone()
    assert row[0] is None
    assert row[1] is None


def test_dim_event_row_count(loaded_silver):
    with loaded_silver.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM silver.dim_event")).scalar()
    assert count == 3


def test_dim_event_start_time_is_timestamp(loaded_silver):
    from datetime import datetime
    with loaded_silver.connect() as conn:
        row = conn.execute(text(
            "SELECT start_time FROM silver.dim_event WHERE event_id = 101"
        )).fetchone()
    assert isinstance(row[0], datetime)
```

- [ ] **Step 2: Rodar testes para ver falhar**

```bash
uv run pytest tests/test_silver.py::test_dim_customer_row_count -v
```

Esperado: FAIL — `ImportError` ou `ProgrammingError: relation "silver.dim_customer" is empty`

- [ ] **Step 3: Criar `src/transformation/silver.py` com dim_customer e dim_event**

```python
import pandas as pd
from sqlalchemy import text

_SQL_DIM_CUSTOMER = """
TRUNCATE silver.dim_customer;
INSERT INTO silver.dim_customer
    (customer_id, registration_date, gender, birth_date, age, ingested_at)
SELECT
    customer_id::INTEGER,
    TO_DATE(customer_datecreation_id, 'YYYYMMDD'),
    NULLIF(customer_gender_name, ''),
    NULLIF(customer_birthday, '')::TIMESTAMPTZ::DATE,
    EXTRACT(YEAR FROM AGE(NOW(), NULLIF(customer_birthday, '')::TIMESTAMPTZ::DATE))::INTEGER,
    NOW()
FROM bronze.customer
WHERE customer_id ~ '^[0-9]+$';
"""

_SQL_DIM_EVENT = """
TRUNCATE silver.dim_event;
INSERT INTO silver.dim_event
    (event_id, sport_name, class_name, type_name, event_name, start_time, end_time, ingested_at)
SELECT
    event_id::INTEGER,
    NULLIF(event_sport_name, ''),
    NULLIF(event_class_name, ''),
    NULLIF(event_type_name, ''),
    NULLIF(event_name, ''),
    NULLIF(event_start_time, '')::TIMESTAMPTZ::TIMESTAMP,
    NULLIF(event_end_time, '')::TIMESTAMPTZ::TIMESTAMP,
    NOW()
FROM bronze.events
WHERE event_id ~ '^[0-9]+$';
"""


def _populate_dim_customer(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_DIM_CUSTOMER))


def _populate_dim_event(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_DIM_EVENT))


def populate_silver(engine) -> None:
    print("Silver: dim_customer...")
    _populate_dim_customer(engine)
    print("Silver: dim_event...")
    _populate_dim_event(engine)
```

- [ ] **Step 4: Rodar testes**

```bash
uv run pytest tests/test_silver.py -k "dim_customer or dim_event" -v
```

Esperado: 7 testes PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/transformation/silver.py tests/test_silver.py
git commit -m "feat: Silver dim_customer e dim_event (TDD)"
```

---

### Task 6: Silver — dim_crm_level com forward-fill (TDD)

**Files:**
- Modify: `tests/test_silver.py` (adicionar testes)
- Modify: `src/transformation/silver.py` (adicionar função)

- [ ] **Step 1: Adicionar testes de forward-fill**

Adicionar ao final de `tests/test_silver.py`:

```python
def test_dim_crm_level_forward_fill(loaded_silver):
    """Cliente 1 tem Bronze em Set/2018 e Silver em Jan/2019.
    Os meses Out, Nov, Dez/2018 devem ser Bronze (forward-fill)."""
    from datetime import date
    with loaded_silver.connect() as conn:
        rows = conn.execute(text("""
            SELECT year_month, crm_level
            FROM silver.dim_crm_level
            WHERE customer_id = 1
            ORDER BY year_month
        """)).fetchall()
    months = {r[0]: r[1] for r in rows}
    assert months[date(2018, 10, 1)] == 'Bronze'
    assert months[date(2018, 11, 1)] == 'Bronze'
    assert months[date(2018, 12, 1)] == 'Bronze'
    assert months[date(2019, 1, 1)] == 'Silver'


def test_dim_crm_level_no_months_before_first_record(loaded_silver):
    """dim_crm_level não deve ter meses anteriores ao primeiro registro."""
    from datetime import date
    with loaded_silver.connect() as conn:
        row = conn.execute(text("""
            SELECT MIN(year_month) FROM silver.dim_crm_level WHERE customer_id = 1
        """)).scalar()
    assert row == date(2018, 9, 1)


def test_dim_crm_level_pk_unique(loaded_silver):
    with loaded_silver.connect() as conn:
        count = conn.execute(text("""
            SELECT COUNT(*) FROM (
                SELECT customer_id, year_month, COUNT(*)
                FROM silver.dim_crm_level
                GROUP BY customer_id, year_month
                HAVING COUNT(*) > 1
            ) dups
        """)).scalar()
    assert count == 0
```

- [ ] **Step 2: Rodar testes para ver falhar**

```bash
uv run pytest tests/test_silver.py -k "crm_level" -v
```

Esperado: FAIL — `AssertionError` (tabela vazia, populate_silver ainda não chama dim_crm_level)

- [ ] **Step 3: Adicionar `_populate_dim_crm_level` em `silver.py`**

Adicionar antes de `populate_silver`:

```python
def _populate_dim_crm_level(engine) -> None:
    df = pd.read_sql(
        "SELECT customer_id, date_yearmonth, crm_level FROM bronze.customer_crm_level",
        engine
    )
    df['customer_id'] = df['customer_id'].astype(int)
    # date_yearmonth está no formato YYYYMM (ex: 201902) — converter para primeiro dia do mês
    df['year_month'] = pd.to_datetime(
        df['date_yearmonth'].astype(str) + '01', format='%Y%m%d'
    )

    season_end = pd.Timestamp('2019-08-01')
    rows = []
    for cid, group in df.groupby('customer_id'):
        series = group.sort_values('year_month').set_index('year_month')['crm_level']
        idx = pd.date_range(series.index.min(), season_end, freq='MS')
        filled = series.reindex(idx).ffill()
        for month, level in filled.items():
            if pd.notna(level):
                rows.append({
                    'customer_id': int(cid),
                    'year_month': month.date(),
                    'crm_level': level,
                })

    result = pd.DataFrame(rows)
    result['ingested_at'] = pd.Timestamp.now()
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE silver.dim_crm_level"))
    result.to_sql('dim_crm_level', engine, schema='silver', if_exists='append', index=False)
```

Atualizar `populate_silver` para chamar a nova função:

```python
def populate_silver(engine) -> None:
    print("Silver: dim_customer...")
    _populate_dim_customer(engine)
    print("Silver: dim_crm_level (forward-fill)...")
    _populate_dim_crm_level(engine)
    print("Silver: dim_event...")
    _populate_dim_event(engine)
```

- [ ] **Step 4: Rodar testes**

```bash
uv run pytest tests/test_silver.py -k "crm_level" -v
```

Esperado: 3 testes PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/transformation/silver.py tests/test_silver.py
git commit -m "feat: Silver dim_crm_level com forward-fill pandas (TDD)"
```

---

### Task 7: Silver — dim_market, dim_channel e dim_date (TDD)

**Files:**
- Modify: `tests/test_silver.py`
- Modify: `src/transformation/silver.py`

- [ ] **Step 1: Adicionar testes**

Adicionar ao final de `tests/test_silver.py`:

```python
def test_dim_market_deduplication(loaded_silver):
    """Match Winner/Single deve aparecer apenas uma vez mesmo com 3 apostas."""
    with loaded_silver.connect() as conn:
        count = conn.execute(text("""
            SELECT COUNT(*) FROM silver.dim_market
            WHERE market_name = 'Match Winner' AND bet_type = 'Single'
        """)).scalar()
    assert count == 1


def test_dim_market_has_surrogate_key(loaded_silver):
    with loaded_silver.connect() as conn:
        row = conn.execute(text(
            "SELECT market_id FROM silver.dim_market LIMIT 1"
        )).fetchone()
    assert row[0] >= 1


def test_dim_channel_row_count(loaded_silver):
    """Android, iOS, Web → 3 canais distintos."""
    with loaded_silver.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM silver.dim_channel")).scalar()
    assert count == 3


def test_dim_date_covers_season(loaded_silver):
    from datetime import date
    with loaded_silver.connect() as conn:
        row = conn.execute(text("""
            SELECT date_id FROM silver.dim_date
            WHERE full_date = '2018-09-01'
        """)).fetchone()
    assert row is not None
    assert row[0] == 20180901


def test_dim_date_is_weekend(loaded_silver):
    """2019-03-09 é Sábado → is_weekend = TRUE."""
    with loaded_silver.connect() as conn:
        row = conn.execute(text("""
            SELECT is_weekend, day_name FROM silver.dim_date
            WHERE full_date = '2019-03-09'
        """)).fetchone()
    assert row[0] is True
    assert row[1] == 'Sábado'


def test_dim_date_month_name_portuguese(loaded_silver):
    with loaded_silver.connect() as conn:
        row = conn.execute(text("""
            SELECT month_name FROM silver.dim_date WHERE full_date = '2018-09-01'
        """)).fetchone()
    assert row[0] == 'Setembro'
```

- [ ] **Step 2: Rodar para ver falhar**

```bash
uv run pytest tests/test_silver.py -k "dim_market or dim_channel or dim_date" -v
```

Esperado: FAIL.

- [ ] **Step 3: Adicionar funções em `silver.py`**

Adicionar constantes de nomes no topo do arquivo (após os imports):

```python
_MONTH_NAMES_PT = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro',
}
_DAY_NAMES_PT = {
    1: 'Segunda', 2: 'Terça', 3: 'Quarta', 4: 'Quinta',
    5: 'Sexta', 6: 'Sábado', 7: 'Domingo',
}
```

Adicionar as três funções antes de `populate_silver`:

```python
_SQL_DIM_MARKET = """
TRUNCATE silver.dim_market RESTART IDENTITY;
INSERT INTO silver.dim_market (market_name, bet_type, ingested_at)
SELECT DISTINCT
    market_template_name,
    NULLIF(bettype_name, ''),
    NOW()
FROM bronze.sportsbook
WHERE market_template_name IS NOT NULL AND market_template_name <> '';
"""

_SQL_DIM_CHANNEL = """
TRUNCATE silver.dim_channel RESTART IDENTITY;
INSERT INTO silver.dim_channel (channel_name, ingested_at)
SELECT DISTINCT channel_name, NOW()
FROM bronze.sportsbook
WHERE channel_name IS NOT NULL AND channel_name <> '';
"""


def _populate_dim_market(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_DIM_MARKET))


def _populate_dim_channel(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_DIM_CHANNEL))


def _populate_dim_date(engine) -> None:
    dates = pd.date_range('2017-07-01', '2019-09-30', freq='D')
    iso_dow = dates.isocalendar().day  # 1=Segunda … 7=Domingo
    df = pd.DataFrame({
        'date_id':      dates.strftime('%Y%m%d').astype(int),
        'full_date':    dates.date,
        'year':         dates.year.astype(int),
        'month':        dates.month.astype(int),
        'month_name':   dates.month.map(_MONTH_NAMES_PT),
        'day':          dates.day.astype(int),
        'day_of_week':  iso_dow.astype(int),
        'day_name':     iso_dow.map(_DAY_NAMES_PT),
        'is_weekend':   (iso_dow >= 6),
        'ingested_at':  pd.Timestamp.now(),
    })
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE silver.dim_date"))
    df.to_sql('dim_date', engine, schema='silver', if_exists='append', index=False)
```

Atualizar `populate_silver`:

```python
def populate_silver(engine) -> None:
    print("Silver: dim_customer...")
    _populate_dim_customer(engine)
    print("Silver: dim_crm_level (forward-fill)...")
    _populate_dim_crm_level(engine)
    print("Silver: dim_event...")
    _populate_dim_event(engine)
    print("Silver: dim_market...")
    _populate_dim_market(engine)
    print("Silver: dim_channel...")
    _populate_dim_channel(engine)
    print("Silver: dim_date...")
    _populate_dim_date(engine)
```

- [ ] **Step 4: Rodar testes**

```bash
uv run pytest tests/test_silver.py -k "dim_market or dim_channel or dim_date" -v
```

Esperado: 6 testes PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/transformation/silver.py tests/test_silver.py
git commit -m "feat: Silver dim_market, dim_channel, dim_date (TDD)"
```

---

### Task 8: Silver — fact_bets (TDD)

**Files:**
- Modify: `tests/test_silver.py`
- Modify: `src/transformation/silver.py`

- [ ] **Step 1: Adicionar testes de fact_bets**

Adicionar ao final de `tests/test_silver.py`:

```python
def test_fact_bets_row_count(loaded_silver):
    with loaded_silver.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM silver.fact_bets")).scalar()
    assert count == 8


def test_fact_bets_gross_revenue(loaded_silver):
    """BET001: turnover=10.00, winnings=0.00 → gross_revenue=10.00"""
    with loaded_silver.connect() as conn:
        row = conn.execute(text("""
            SELECT turnover, winnings, gross_revenue
            FROM silver.fact_bets WHERE bet_id = 'BET001'
        """)).fetchone()
    from decimal import Decimal
    assert row[2] == row[0] - row[1]
    assert row[2] == Decimal('10.00')


def test_fact_bets_is_live_false(loaded_silver):
    """BET001: placed 17:30, event starts 18:00 → is_live = FALSE"""
    with loaded_silver.connect() as conn:
        row = conn.execute(text(
            "SELECT is_live FROM silver.fact_bets WHERE bet_id = 'BET001'"
        )).fetchone()
    assert row[0] is False


def test_fact_bets_is_live_true(loaded_silver):
    """BET002: placed 19:00, event starts 18:00 → is_live = TRUE"""
    with loaded_silver.connect() as conn:
        row = conn.execute(text(
            "SELECT is_live FROM silver.fact_bets WHERE bet_id = 'BET002'"
        )).fetchone()
    assert row[0] is True


def test_fact_bets_no_event_is_pre_event(loaded_silver):
    """BET006: sem event_id → is_live = FALSE"""
    with loaded_silver.connect() as conn:
        row = conn.execute(text(
            "SELECT is_live FROM silver.fact_bets WHERE bet_id = 'BET006'"
        )).fetchone()
    assert row[0] is False


def test_fact_bets_date_id_format(loaded_silver):
    """date_id de BET001 (placed 2018-09-15) deve ser 20180915"""
    with loaded_silver.connect() as conn:
        row = conn.execute(text(
            "SELECT date_id FROM silver.fact_bets WHERE bet_id = 'BET001'"
        )).fetchone()
    assert row[0] == 20180915


def test_fact_bets_placed_hour(loaded_silver):
    """BET001 placed às 17:30 → placed_hour = 17"""
    with loaded_silver.connect() as conn:
        row = conn.execute(text(
            "SELECT placed_hour FROM silver.fact_bets WHERE bet_id = 'BET001'"
        )).fetchone()
    assert row[0] == 17
```

- [ ] **Step 2: Rodar para ver falhar**

```bash
uv run pytest tests/test_silver.py -k "fact_bets" -v
```

Esperado: FAIL.

- [ ] **Step 3: Adicionar `_populate_fact_bets` em `silver.py`**

```python
_SQL_FACT_BETS = """
TRUNCATE silver.fact_bets;
INSERT INTO silver.fact_bets
    (bet_id, customer_id, event_id, date_id, market_id, channel_id,
     placed_at, settled_at, placed_hour, turnover, winnings, gross_revenue, is_live, ingested_at)
SELECT
    sb.sportbetsettled_bet_id,
    sb.sportbetsettled_customer_id::INTEGER,
    NULLIF(sb.sportbetsettled_event_id, '')::INTEGER,
    TO_CHAR(sb.sportbetsettled_placed::TIMESTAMPTZ::TIMESTAMP, 'YYYYMMDD')::INTEGER,
    dm.market_id,
    dc.channel_id,
    sb.sportbetsettled_placed::TIMESTAMPTZ::TIMESTAMP,
    NULLIF(sb.sportbetsettled_settled, '')::TIMESTAMPTZ::TIMESTAMP,
    EXTRACT(HOUR FROM sb.sportbetsettled_placed::TIMESTAMPTZ::TIMESTAMP)::INTEGER,
    sb.turnover::NUMERIC(12,2),
    sb.winnings::NUMERIC(12,2),
    sb.turnover::NUMERIC(12,2) - sb.winnings::NUMERIC(12,2),
    sb.sportbetsettled_placed::TIMESTAMPTZ::TIMESTAMP
        >= COALESCE(de.start_time, 'infinity'::TIMESTAMP),
    NOW()
FROM bronze.sportsbook sb
LEFT JOIN silver.dim_market dm
    ON dm.market_name = sb.market_template_name
    AND (
        dm.bet_type = NULLIF(sb.bettype_name, '')
        OR (dm.bet_type IS NULL AND NULLIF(sb.bettype_name, '') IS NULL)
    )
LEFT JOIN silver.dim_channel dc
    ON dc.channel_name = sb.channel_name
LEFT JOIN silver.dim_event de
    ON de.event_id = NULLIF(sb.sportbetsettled_event_id, '')::INTEGER
WHERE sb.sportbetsettled_bet_id IS NOT NULL;
"""


def _populate_fact_bets(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_FACT_BETS))
```

Atualizar `populate_silver`:

```python
def populate_silver(engine) -> None:
    print("Silver: dim_customer...")
    _populate_dim_customer(engine)
    print("Silver: dim_crm_level (forward-fill)...")
    _populate_dim_crm_level(engine)
    print("Silver: dim_event...")
    _populate_dim_event(engine)
    print("Silver: dim_market...")
    _populate_dim_market(engine)
    print("Silver: dim_channel...")
    _populate_dim_channel(engine)
    print("Silver: dim_date...")
    _populate_dim_date(engine)
    print("Silver: fact_bets...")
    _populate_fact_bets(engine)
```

- [ ] **Step 4: Rodar testes**

```bash
uv run pytest tests/test_silver.py -k "fact_bets" -v
```

Esperado: 7 testes PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/transformation/silver.py tests/test_silver.py
git commit -m "feat: Silver fact_bets com is_live e gross_revenue (TDD)"
```

---

### Task 9: Silver — fact_cashouts, populate_silver completo e run_silver.py

**Files:**
- Modify: `tests/test_silver.py`
- Modify: `src/transformation/silver.py`
- Create: `src/transformation/run_silver.py`

- [ ] **Step 1: Adicionar testes de fact_cashouts**

Adicionar ao final de `tests/test_silver.py`:

```python
def test_fact_cashouts_row_count(loaded_silver):
    with loaded_silver.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM silver.fact_cashouts")).scalar()
    assert count == 3


def test_fact_cashouts_date_id_format(loaded_silver):
    """CO001 criado em 2018-10-20 → date_id = 20181020"""
    with loaded_silver.connect() as conn:
        row = conn.execute(text(
            "SELECT date_id FROM silver.fact_cashouts WHERE cashout_id = 'CO001'"
        )).fetchone()
    assert row[0] == 20181020


def test_fact_cashouts_amount_nullable(loaded_silver):
    """CO002 (Failed) tem amount NULL."""
    with loaded_silver.connect() as conn:
        row = conn.execute(text(
            "SELECT cashout_amount FROM silver.fact_cashouts WHERE cashout_id = 'CO002'"
        )).fetchone()
    assert row[0] is None
```

- [ ] **Step 2: Rodar para ver falhar**

```bash
uv run pytest tests/test_silver.py -k "cashout" -v
```

Esperado: FAIL.

- [ ] **Step 3: Adicionar `_populate_fact_cashouts` e finalizar `populate_silver`**

Adicionar em `silver.py`:

```python
_SQL_FACT_CASHOUTS = """
TRUNCATE silver.fact_cashouts;
INSERT INTO silver.fact_cashouts
    (cashout_id, bet_id, date_id, created_at, status, cashout_amount, ingested_at)
SELECT
    cashout_attempt_bet_cashout_id,
    cashout_attempt_bet_id,
    TO_CHAR(
        cashout_attempt_bet_cashout_created::TIMESTAMPTZ::TIMESTAMP,
        'YYYYMMDD'
    )::INTEGER,
    cashout_attempt_bet_cashout_created::TIMESTAMPTZ::TIMESTAMP,
    cashout_attempt_bet_cashout_status,
    NULLIF(cashout_attempt_cashout_amount, '')::NUMERIC(12,2),
    NOW()
FROM bronze.cashouts
WHERE cashout_attempt_bet_cashout_id IS NOT NULL;
"""


def _populate_fact_cashouts(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_FACT_CASHOUTS))
```

Atualizar `populate_silver` para a versão final:

```python
def populate_silver(engine) -> None:
    print("Silver: dim_customer...")
    _populate_dim_customer(engine)
    print("Silver: dim_crm_level (forward-fill)...")
    _populate_dim_crm_level(engine)
    print("Silver: dim_event...")
    _populate_dim_event(engine)
    print("Silver: dim_market...")
    _populate_dim_market(engine)
    print("Silver: dim_channel...")
    _populate_dim_channel(engine)
    print("Silver: dim_date...")
    _populate_dim_date(engine)
    print("Silver: fact_bets...")
    _populate_fact_bets(engine)
    print("Silver: fact_cashouts...")
    _populate_fact_cashouts(engine)
    print("Silver: concluído.")
```

- [ ] **Step 4: Criar `src/transformation/run_silver.py`**

```python
from src.db import get_engine
from src.transformation.silver import populate_silver

if __name__ == "__main__":
    engine = get_engine()
    print("Iniciando transformação Silver...")
    populate_silver(engine)
    print("Transformação Silver concluída.")
```

- [ ] **Step 5: Rodar todos os testes Silver**

```bash
uv run pytest tests/test_silver.py -v
```

Esperado: todos os testes Silver PASSED (≥ 23 testes).

- [ ] **Step 6: Commit**

```bash
git add src/transformation/silver.py src/transformation/run_silver.py tests/test_silver.py
git commit -m "feat: Silver fact_cashouts + populate_silver completo + run_silver.py (TDD)"
```

---

### Task 10: Gold — customer_performance e customer_segments (TDD)

**Files:**
- Create: `tests/test_gold.py` (parcial)
- Create: `src/transformation/gold.py` (parcial)

- [ ] **Step 1: Escrever testes**

```python
# tests/test_gold.py
from decimal import Decimal
from sqlalchemy import text


def test_customer_performance_gross_revenue(loaded_gold):
    """Customer 1: BET001 (GR=10) + BET002 (GR=-10) + BET007 (GR=5) = 5.00"""
    with loaded_gold.connect() as conn:
        row = conn.execute(text("""
            SELECT gross_revenue FROM gold.customer_performance
            WHERE customer_id = 1
        """)).fetchone()
    assert row[0] == Decimal('5.00')


def test_customer_performance_live_bets(loaded_gold):
    """Customer 1: BET002 é live → live_bets = 1"""
    with loaded_gold.connect() as conn:
        row = conn.execute(text("""
            SELECT live_bets, pre_event_bets
            FROM gold.customer_performance WHERE customer_id = 1
        """)).fetchone()
    assert row[0] == 1   # BET002 (live)
    assert row[1] == 2   # BET001, BET007 (pre-event)


def test_customer_performance_cashouts(loaded_gold):
    """Customer 1 tem 1 cashout attempt (CO002, Failed) → successful=0"""
    with loaded_gold.connect() as conn:
        row = conn.execute(text("""
            SELECT cashout_attempts, successful_cashouts
            FROM gold.customer_performance WHERE customer_id = 1
        """)).fetchone()
    assert row[0] == 1
    assert row[1] == 0


def test_customer_segment_existente(loaded_gold):
    """Customer 1: bets antes (BET007, Apr 2018) E durante a temporada → existente"""
    with loaded_gold.connect() as conn:
        row = conn.execute(text("""
            SELECT segment FROM gold.customer_segments WHERE customer_id = 1
        """)).fetchone()
    assert row[0] == 'existente'


def test_customer_segment_novo(loaded_gold):
    """Customer 2: só tem bets dentro da temporada → novo"""
    with loaded_gold.connect() as conn:
        row = conn.execute(text(
            "SELECT segment FROM gold.customer_segments WHERE customer_id = 2"
        )).fetchone()
    assert row[0] == 'novo'


def test_customer_segment_saindo(loaded_gold):
    """Customer 4: pre-season (BET008 Jul 2018) + in-season (BET005 Sep 2018)
    + sem bets Jun-Ago 2019 → saindo"""
    with loaded_gold.connect() as conn:
        row = conn.execute(text(
            "SELECT segment FROM gold.customer_segments WHERE customer_id = 4"
        )).fetchone()
    assert row[0] == 'saindo'
```

- [ ] **Step 2: Rodar para ver falhar**

```bash
uv run pytest tests/test_gold.py -v
```

Esperado: FAIL — `ImportError`.

- [ ] **Step 3: Criar `src/transformation/gold.py` com as duas primeiras funções**

```python
from sqlalchemy import text

_SQL_CUSTOMER_PERFORMANCE = """
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
    COUNT(fc.cashout_id) FILTER (WHERE fc.status = 'Successful'),
    NOW()
FROM silver.dim_customer dc
LEFT JOIN silver.fact_bets fb ON fb.customer_id = dc.customer_id
LEFT JOIN silver.fact_cashouts fc ON fc.bet_id = fb.bet_id
GROUP BY dc.customer_id, dc.gender, dc.age;
"""

_SQL_CUSTOMER_SEGMENTS = """
TRUNCATE gold.customer_segments;
INSERT INTO gold.customer_segments
    (customer_id, segment, first_bet_date, last_bet_date, crm_level, updated_at)
WITH activity AS (
    SELECT
        customer_id,
        MIN(placed_at::DATE)                                                    AS first_bet_date,
        MAX(placed_at::DATE)                                                    AS last_bet_date,
        BOOL_OR(placed_at >= '2018-09-01' AND placed_at < '2019-09-01')        AS in_season,
        BOOL_OR(placed_at < '2018-09-01')                                       AS pre_season,
        BOOL_OR(placed_at >= '2019-06-01' AND placed_at < '2019-09-01')        AS last_3_months
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
        WHEN a.in_season AND NOT a.pre_season     THEN 'novo'
        WHEN a.in_season AND a.pre_season         THEN 'existente'
        WHEN a.pre_season AND NOT a.last_3_months THEN 'saindo'
        ELSE 'novo'
    END,
    a.first_bet_date,
    a.last_bet_date,
    cl.crm_level,
    NOW()
FROM activity a
LEFT JOIN crm_latest cl ON cl.customer_id = a.customer_id
WHERE a.in_season OR a.pre_season;
"""


def _populate_customer_performance(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_CUSTOMER_PERFORMANCE))


def _populate_customer_segments(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_CUSTOMER_SEGMENTS))


def populate_gold(engine) -> None:
    print("Gold: customer_performance...")
    _populate_customer_performance(engine)
    print("Gold: customer_segments...")
    _populate_customer_segments(engine)
```

- [ ] **Step 4: Rodar testes**

```bash
uv run pytest tests/test_gold.py -v
```

Esperado: 6 testes PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/transformation/gold.py tests/test_gold.py
git commit -m "feat: Gold customer_performance e customer_segments (TDD)"
```

---

### Task 11: Gold — betting_preferences e crm_performance (TDD)

**Files:**
- Modify: `tests/test_gold.py`
- Modify: `src/transformation/gold.py`

- [ ] **Step 1: Adicionar testes**

Adicionar ao final de `tests/test_gold.py`:

```python
def test_betting_preferences_preferred_channel(loaded_gold):
    """Customer 1 apostou 2x no Android → preferred_channel = Android"""
    with loaded_gold.connect() as conn:
        row = conn.execute(text("""
            SELECT preferred_channel FROM gold.betting_preferences WHERE customer_id = 1
        """)).fetchone()
    assert row[0] == 'Android'


def test_betting_preferences_live_pct(loaded_gold):
    """Customer 1: 3 apostas, 1 live → live_bet_pct = 33.33"""
    with loaded_gold.connect() as conn:
        row = conn.execute(text("""
            SELECT live_bet_pct FROM gold.betting_preferences WHERE customer_id = 1
        """)).fetchone()
    assert float(row[0]) == pytest.approx(33.33, abs=0.01)


def test_crm_performance_bronze_exists(loaded_gold):
    with loaded_gold.connect() as conn:
        row = conn.execute(text("""
            SELECT crm_level, total_bets FROM gold.crm_performance
            WHERE crm_level = 'Bronze'
        """)).fetchone()
    assert row is not None
    assert row[1] > 0
```

Adicionar `import pytest` ao topo de `tests/test_gold.py`.

- [ ] **Step 2: Rodar para ver falhar**

```bash
uv run pytest tests/test_gold.py -k "preferences or crm_performance" -v
```

Esperado: FAIL.

- [ ] **Step 3: Adicionar funções em `gold.py`**

```python
_SQL_BETTING_PREFERENCES = """
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
"""

_SQL_CRM_PERFORMANCE = """
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
    ROUND(COUNT(fb.bet_id)::NUMERIC      / NULLIF(COUNT(DISTINCT fb.customer_id), 0), 2),
    ROUND(SUM(fb.turnover)::NUMERIC      / NULLIF(COUNT(DISTINCT fb.customer_id), 0), 2),
    ROUND(SUM(fb.gross_revenue)::NUMERIC / NULLIF(COUNT(DISTINCT fb.customer_id), 0), 2),
    NOW()
FROM silver.fact_bets fb
JOIN silver.dim_crm_level dcl
    ON dcl.customer_id = fb.customer_id
    AND dcl.year_month = DATE_TRUNC('month', fb.placed_at)::DATE
GROUP BY dcl.crm_level;
"""


def _populate_betting_preferences(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_BETTING_PREFERENCES))


def _populate_crm_performance(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_CRM_PERFORMANCE))
```

Atualizar `populate_gold`:

```python
def populate_gold(engine) -> None:
    print("Gold: customer_performance...")
    _populate_customer_performance(engine)
    print("Gold: customer_segments...")
    _populate_customer_segments(engine)
    print("Gold: betting_preferences...")
    _populate_betting_preferences(engine)
    print("Gold: crm_performance...")
    _populate_crm_performance(engine)
```

- [ ] **Step 4: Rodar testes**

```bash
uv run pytest tests/test_gold.py -k "preferences or crm_performance" -v
```

Esperado: 3 testes PASSED.

- [ ] **Step 5: Commit**

```bash
git add src/transformation/gold.py tests/test_gold.py
git commit -m "feat: Gold betting_preferences e crm_performance (TDD)"
```

---

### Task 12: Gold — season_summary, cashout_analysis, populate_gold completo e run_gold.py

**Files:**
- Modify: `tests/test_gold.py`
- Modify: `src/transformation/gold.py`
- Create: `src/transformation/run_gold.py`

- [ ] **Step 1: Adicionar testes**

Adicionar ao final de `tests/test_gold.py`:

```python
def test_season_summary_gross_revenue_consistency(loaded_gold):
    """Soma de gross_revenue em season_summary deve bater com fact_bets (período da temporada)."""
    with loaded_gold.connect() as conn:
        gold_total = conn.execute(text(
            "SELECT SUM(gross_revenue) FROM gold.season_summary"
        )).scalar()
        silver_total = conn.execute(text("""
            SELECT SUM(gross_revenue) FROM silver.fact_bets
            WHERE placed_at >= '2018-09-01' AND placed_at < '2019-09-01'
        """)).scalar()
    assert gold_total == silver_total


def test_cashout_analysis_success_rate(loaded_gold):
    """Out/2018: CO001 (Successful), sem outros → success_rate = 100.00"""
    from datetime import date
    with loaded_gold.connect() as conn:
        row = conn.execute(text("""
            SELECT success_rate, total_attempts, successful_attempts
            FROM gold.cashout_analysis
            WHERE month = '2018-10-01'
        """)).fetchone()
    assert row is not None
    assert float(row[0]) == pytest.approx(100.0, abs=0.01)
    assert row[1] == 1
    assert row[2] == 1


def test_cashout_analysis_failed_counted(loaded_gold):
    """Set/2018: CO002 (Failed) + CO003 (Successful) → total=2, failed=1"""
    with loaded_gold.connect() as conn:
        row = conn.execute(text("""
            SELECT total_attempts, failed_attempts
            FROM gold.cashout_analysis
            WHERE month = '2018-09-01'
        """)).fetchone()
    assert row[0] == 2
    assert row[1] == 1
```

- [ ] **Step 2: Rodar para ver falhar**

```bash
uv run pytest tests/test_gold.py -k "season or cashout_analysis" -v
```

Esperado: FAIL.

- [ ] **Step 3: Adicionar funções e finalizar `gold.py`**

```python
_SQL_SEASON_SUMMARY = """
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
    0,
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
"""

_SQL_CASHOUT_ANALYSIS = """
TRUNCATE gold.cashout_analysis;
INSERT INTO gold.cashout_analysis
    (month, total_attempts, successful_attempts, failed_attempts,
     success_rate, total_cashout_amount, avg_cashout_amount, updated_at)
SELECT
    DATE_TRUNC('month', fc.created_at)::DATE,
    COUNT(*),
    COUNT(*) FILTER (WHERE fc.status = 'Successful'),
    COUNT(*) FILTER (WHERE fc.status <> 'Successful'),
    ROUND(AVG((fc.status = 'Successful')::INT) * 100, 2),
    COALESCE(SUM(fc.cashout_amount), 0),
    COALESCE(ROUND(AVG(fc.cashout_amount), 2), 0),
    NOW()
FROM silver.fact_cashouts fc
WHERE fc.created_at >= '2018-09-01' AND fc.created_at < '2019-09-01'
GROUP BY DATE_TRUNC('month', fc.created_at)::DATE
ORDER BY 1;
"""


def _populate_season_summary(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_SEASON_SUMMARY))


def _populate_cashout_analysis(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_CASHOUT_ANALYSIS))
```

Versão final de `populate_gold`:

```python
def populate_gold(engine) -> None:
    print("Gold: customer_performance...")
    _populate_customer_performance(engine)
    print("Gold: customer_segments...")
    _populate_customer_segments(engine)
    print("Gold: betting_preferences...")
    _populate_betting_preferences(engine)
    print("Gold: crm_performance...")
    _populate_crm_performance(engine)
    print("Gold: season_summary...")
    _populate_season_summary(engine)
    print("Gold: cashout_analysis...")
    _populate_cashout_analysis(engine)
    print("Gold: concluído.")
```

- [ ] **Step 4: Criar `src/transformation/run_gold.py`**

```python
from src.db import get_engine
from src.transformation.gold import populate_gold

if __name__ == "__main__":
    engine = get_engine()
    print("Iniciando transformação Gold...")
    populate_gold(engine)
    print("Transformação Gold concluída.")
```

- [ ] **Step 5: Rodar todos os testes**

```bash
uv run pytest tests/ -v
```

Esperado: todos os testes PASSED (≥ 32 testes no total).

- [ ] **Step 6: Commit**

```bash
git add src/transformation/gold.py src/transformation/run_gold.py tests/test_gold.py
git commit -m "feat: Gold season_summary, cashout_analysis + populate_gold completo + run_gold.py (TDD)"
```

---

### Task 13: Teste end-to-end com dados reais e push

**Files:** nenhum novo

- [ ] **Step 1: Garantir Docker rodando com banco limpo**

```bash
docker compose down -v
docker compose up -d postgres
sleep 5
```

- [ ] **Step 2: Rodar pipeline completo com dados reais**

```bash
uv run python src/ingestion/run_ingestion.py
uv run python src/transformation/run_silver.py
uv run python src/transformation/run_gold.py
```

Esperado: nenhum erro, output de progresso para cada tabela.

- [ ] **Step 3: Verificar contagens no banco**

```bash
docker compose exec postgres psql -U sportsbook -d sportsbook_db -c "
SELECT schemaname, tablename, n_live_tup AS linhas
FROM pg_stat_user_tables
WHERE schemaname IN ('bronze','silver','gold')
ORDER BY schemaname, tablename;
"
```

Esperado: todas as tabelas com contagem > 0. bronze.sportsbook ≈ 1.499.459, silver.fact_bets similar, gold.season_summary = 12 linhas (Set/2018 a Ago/2019).

- [ ] **Step 4: Verificar regras de negócio nos dados reais**

```bash
docker compose exec postgres psql -U sportsbook -d sportsbook_db -c "
SELECT
  COUNT(*) AS total_bets,
  COUNT(*) FILTER (WHERE is_live) AS live_bets,
  SUM(gross_revenue) AS total_gr
FROM silver.fact_bets;
"
```

```bash
docker compose exec postgres psql -U sportsbook -d sportsbook_db -c "
SELECT segment, COUNT(*) FROM gold.customer_segments GROUP BY segment ORDER BY segment;
"
```

Esperado: segmentos novo/existente/saindo com contagens plausíveis (não zero).

- [ ] **Step 5: Rodar todos os testes uma última vez**

```bash
uv run pytest tests/ -v --tb=short
```

Esperado: todos os testes PASSED.

- [ ] **Step 6: Push para o GitHub**

```bash
git push origin main
```
