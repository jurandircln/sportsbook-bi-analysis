from src.db import get_engine
from src.transformation.gold import populate_gold

if __name__ == "__main__":
    engine = get_engine()
    print("Iniciando transformação Gold...")
    populate_gold(engine)
    print("Transformação Gold concluída.")
