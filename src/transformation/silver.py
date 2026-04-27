import pandas as pd
from sqlalchemy import text

_MONTH_NAMES_PT = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro',
}
_DAY_NAMES_PT = {
    1: 'Segunda', 2: 'Terça', 3: 'Quarta', 4: 'Quinta',
    5: 'Sexta', 6: 'Sábado', 7: 'Domingo',
}

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

_CHUNK_SIZE = 100_000

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


def _populate_dim_customer(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_DIM_CUSTOMER))


def _populate_dim_event(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_DIM_EVENT))


def _populate_dim_crm_level(engine) -> None:
    df = pd.read_sql(
        "SELECT customer_id, date_yearmonth, crm_level FROM bronze.customer_crm_level",
        engine
    )
    df['customer_id'] = df['customer_id'].astype(int)
    # date_yearmonth formato YYYYMM — converter para primeiro dia do mês
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
        'date_id':     dates.strftime('%Y%m%d').astype(int),
        'full_date':   dates.date,
        'year':        dates.year.astype(int),
        'month':       dates.month.astype(int),
        'month_name':  dates.month.map(_MONTH_NAMES_PT),
        'day':         dates.day.astype(int),
        'day_of_week': iso_dow.astype(int),
        'day_name':    iso_dow.map(_DAY_NAMES_PT),
        'is_weekend':  (iso_dow >= 6),
        'ingested_at': pd.Timestamp.now(),
    })
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE silver.dim_date"))
    df.to_sql('dim_date', engine, schema='silver', if_exists='append', index=False)


def _populate_fact_bets(engine) -> None:
    # Pré-carrega dimensões pequenas para lookup em memória
    with engine.connect() as conn:
        markets = pd.read_sql(
            "SELECT market_id, market_name, bet_type FROM silver.dim_market", conn
        )
        channels = pd.read_sql(
            "SELECT channel_id, channel_name FROM silver.dim_channel", conn
        )
        events = pd.read_sql(
            "SELECT event_id, start_time FROM silver.dim_event", conn
        )

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE silver.fact_bets"))

    now = pd.Timestamp.now()

    for i, chunk in enumerate(pd.read_sql(
        "SELECT * FROM bronze.sportsbook WHERE sportbetsettled_bet_id IS NOT NULL",
        engine,
        chunksize=_CHUNK_SIZE,
    )):
        chunk = chunk.rename(columns={
            'sportbetsettled_bet_id': 'bet_id',
            'sportbetsettled_customer_id': 'customer_id',
            'sportbetsettled_event_id': 'event_id_raw',
            'sportbetsettled_placed': 'placed_at_raw',
            'sportbetsettled_settled': 'settled_at_raw',
            'market_template_name': 'market_name',
            'bettype_name': 'bet_type',
            'turnover': 'turnover_raw',
            'winnings': 'winnings_raw',
        })

        chunk['customer_id'] = pd.to_numeric(chunk['customer_id'], errors='coerce').astype('Int64')
        chunk['event_id'] = pd.to_numeric(chunk['event_id_raw'].replace('', pd.NA), errors='coerce').astype('Int64')
        chunk['placed_at'] = pd.to_datetime(chunk['placed_at_raw'], utc=True).dt.tz_localize(None)
        chunk['settled_at'] = pd.to_datetime(chunk['settled_at_raw'].replace('', pd.NA), errors='coerce', utc=True).dt.tz_localize(None)
        chunk['placed_hour'] = chunk['placed_at'].dt.hour
        chunk['date_id'] = chunk['placed_at'].dt.strftime('%Y%m%d').astype(int)
        chunk['turnover'] = pd.to_numeric(chunk['turnover_raw'], errors='coerce').round(2)
        chunk['winnings'] = pd.to_numeric(chunk['winnings_raw'], errors='coerce').round(2)
        chunk['gross_revenue'] = (chunk['turnover'] - chunk['winnings']).round(2)

        # Lookup market_id
        chunk['bet_type'] = chunk['bet_type'].replace('', pd.NA)
        chunk = chunk.merge(markets, on=['market_name', 'bet_type'], how='left')

        # Lookup channel_id
        chunk = chunk.merge(channels, on='channel_name', how='left')

        # Lookup event start_time para is_live
        chunk = chunk.merge(events, left_on='event_id', right_on='event_id', how='left')
        # start_time=NaT → event inexistente → is_live=False (placed_at nunca >= inf)
        chunk['is_live'] = chunk.apply(
            lambda r: bool(r['placed_at'] >= r['start_time']) if pd.notna(r['start_time']) else False,
            axis=1,
        )

        chunk['ingested_at'] = now

        out = chunk[['bet_id', 'customer_id', 'event_id', 'date_id', 'market_id', 'channel_id',
                     'placed_at', 'settled_at', 'placed_hour', 'turnover', 'winnings',
                     'gross_revenue', 'is_live', 'ingested_at']]
        out.to_sql('fact_bets', engine, schema='silver', if_exists='append', index=False,
                   method='multi', chunksize=10_000)
        print(f"  batch {i+1}: {len(chunk):,} linhas")
        del chunk, out


def _populate_fact_cashouts(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_FACT_CASHOUTS))


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
