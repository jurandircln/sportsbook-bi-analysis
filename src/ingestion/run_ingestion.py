from pathlib import Path
from src.db import get_engine
from src.ingestion.loader import load_all_csvs_to_bronze

if __name__ == "__main__":
    engine = get_engine()
    data_dir = Path(__file__).parent.parent.parent / "data" / "raw"
    print("Iniciando ingestão Bronze...")
    load_all_csvs_to_bronze(engine, data_dir)
    print("Ingestão concluída.")
