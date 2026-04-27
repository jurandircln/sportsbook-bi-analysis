from sqlalchemy import text


def test_bronze_customer_row_count(loaded_bronze):
    with loaded_bronze.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM bronze.customer")).scalar()
    assert count == 5


def test_bronze_sportsbook_row_count(loaded_bronze):
    with loaded_bronze.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM bronze.sportsbook")).scalar()
    assert count == 7


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
