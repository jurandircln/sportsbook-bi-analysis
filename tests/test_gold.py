import pytest
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
