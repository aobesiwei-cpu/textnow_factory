from sqlalchemy.orm import declarative_base
from config.db_config import SessionLocal, engine

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()