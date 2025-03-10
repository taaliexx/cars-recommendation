from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Numeric, TIMESTAMP, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import uuid
from globals import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()