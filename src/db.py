from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


def get_engine():
    load_dotenv()
    url = os.environ["DATABASE_URL"]
    return create_engine(url)
