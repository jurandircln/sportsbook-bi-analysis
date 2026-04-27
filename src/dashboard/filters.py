import pandas as pd
from datetime import date


def filter_by_month_range(
    df: pd.DataFrame, col: str, start: date, end: date
) -> pd.DataFrame:
    months = df[col].dt.date
    return df[(months >= start) & (months <= end)]


def filter_by_values(df: pd.DataFrame, col: str, values: list) -> pd.DataFrame:
    if not values:
        return df
    return df[df[col].isin(values)]
