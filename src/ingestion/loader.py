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
        'customer':           _load(engine, data_dir / 'Customer.csv',           'customer',           _CUSTOMER_RENAME),
        'customer_crm_level': _load(engine, data_dir / 'Customer_crm_level.csv', 'customer_crm_level', _CRM_RENAME),
        'events':             _load(engine, data_dir / 'Events.csv',              'events',             _EVENTS_RENAME),
        'sportsbook':         _load(engine, data_dir / 'Sportsbook.csv',          'sportsbook',         _SPORTSBOOK_RENAME),
        'cashouts':           _load(engine, data_dir / 'Cashouts.csv',            'cashouts',           _CASHOUTS_RENAME),
    }
    for table, n in counts.items():
        print(f"bronze.{table:25s} → {n:>8,} linhas")
