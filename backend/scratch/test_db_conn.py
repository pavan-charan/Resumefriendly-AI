import sys
import os
from sqlalchemy import create_engine, inspect

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

from app.core.config import settings

def test_conn():
    print(f"Connecting to database url: {settings.DATABASE_URL} ...")
    try:
        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print("[OK] Connected successfully!")
        print(f"Existing tables: {tables}")
        return True
    except Exception as e:
        print(f"[FAIL] Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_conn()
