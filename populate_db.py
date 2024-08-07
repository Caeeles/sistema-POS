from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.db import SessionLocal
from api.models.models import Base, Product, Stock, User, Sales  # Importar as classes do seu módulo de modelos

# Cria uma sessão do banco de dados
db: Session = SessionLocal()

# Atualiza todos os usuários para ter um papel padrão (por exemplo, "vendedor")
users = db.query(User).all()
for user in users:
    user.role = "gerente"  # ou qualquer valor padrão apropriado
db.commit()

# Fecha a sessão do banco de dados
db.close()