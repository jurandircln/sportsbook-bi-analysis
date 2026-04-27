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
