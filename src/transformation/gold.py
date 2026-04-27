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
        WHEN a.pre_season AND NOT a.in_season     THEN 'saindo'
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


def _populate_customer_performance(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_CUSTOMER_PERFORMANCE))


def _populate_customer_segments(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_CUSTOMER_SEGMENTS))


def _populate_betting_preferences(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_BETTING_PREFERENCES))


def _populate_crm_performance(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_CRM_PERFORMANCE))


def _populate_season_summary(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_SEASON_SUMMARY))


def _populate_cashout_analysis(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(_SQL_CASHOUT_ANALYSIS))


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
