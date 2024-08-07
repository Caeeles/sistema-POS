from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models.models import Base
from contextlib import contextmanager
import os

DATABASE_URL = "sqlite:///pos.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def init_db():
    # Função para inicializar o banco de dados (por exemplo, criar tabelas)
    import api.models  # Certifique-se de importar os modelos para que eles sejam reconhecidos pelo SQLAlchemy
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()