import pandas as pd
from datetime import date
from src.dashboard.filters import filter_by_month_range, filter_by_values


def test_filter_by_month_range_retorna_linhas_no_intervalo():
    df = pd.DataFrame({
        "month": pd.to_datetime(["2018-09-01", "2018-10-01", "2018-11-01"]),
        "value": [1, 2, 3],
    })
    result = filter_by_month_range(df, "month", date(2018, 9, 1), date(2018, 10, 1))
    assert list(result["value"]) == [1, 2]


def test_filter_by_month_range_retorna_vazio_quando_fora_do_intervalo():
    df = pd.DataFrame({
        "month": pd.to_datetime(["2018-09-01"]),
        "value": [1],
    })
    result = filter_by_month_range(df, "month", date(2019, 1, 1), date(2019, 3, 1))
    assert len(result) == 0


def test_filter_by_month_range_retorna_tudo_quando_intervalo_completo():
    df = pd.DataFrame({
        "month": pd.to_datetime(["2018-09-01", "2019-08-01"]),
        "value": [1, 2],
    })
    result = filter_by_month_range(df, "month", date(2018, 9, 1), date(2019, 8, 1))
    assert len(result) == 2


def test_filter_by_values_retorna_linhas_correspondentes():
    df = pd.DataFrame({"crm_level": ["Diamond", "Gold", "Silver"], "v": [1, 2, 3]})
    result = filter_by_values(df, "crm_level", ["Diamond", "Silver"])
    assert list(result["v"]) == [1, 3]


def test_filter_by_values_retorna_tudo_quando_lista_vazia():
    df = pd.DataFrame({"crm_level": ["Diamond", "Gold"], "v": [1, 2]})
    result = filter_by_values(df, "crm_level", [])
    assert len(result) == 2


def test_filter_by_values_retorna_vazio_quando_nenhum_corresponde():
    df = pd.DataFrame({"crm_level": ["Diamond", "Gold"], "v": [1, 2]})
    result = filter_by_values(df, "crm_level", ["Bronze"])
    assert len(result) == 0
