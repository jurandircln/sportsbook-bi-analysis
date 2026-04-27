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


def test_fact_bets_row_count(loaded_silver):
    with loaded_silver.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM silver.fact_bets")).scalar()
    assert count == 7


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
