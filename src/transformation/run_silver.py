from src.db import get_engine
from src.transformation.silver import populate_silver

if __name__ == "__main__":
    engine = get_engine()
    print("Iniciando transformação Silver...")
    populate_silver(engine)
    print("Transformação Silver concluída.")
