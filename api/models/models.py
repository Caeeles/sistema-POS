from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from werkzeug.security import generate_password_hash

Base = declarative_base()

# Tabela Produto
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    pcode = Column(String, unique=True, index=True)
    pname = Column(String, index=True)
    stock = relationship("Stock", back_populates="product", uselist=False)

# Tabela Estoque
class Stock(Base):
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    istock = Column(Integer)
    price = Column(Float)
    sold = Column(Integer)
    odate = Column(DateTime, default=datetime.utcnow)
    discount = Column(Float)
    product = relationship("Product", back_populates="stock")

# Tabela Usuário
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    fname = Column(String)
    lname = Column(String)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    role = Column(String)  # Novo atributo para cargo do usuário
    sales = relationship("Sales", back_populates="user")

    def set_password(self, password):
        self.password = generate_password_hash(password)

# Tabela Vendas
class Sales(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True, index=True)
    sale_date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    total = Column(Float)
    user = relationship("User", back_populates="sales")
    sale_details = relationship("SaleDetails", back_populates="sale")

# Tabela Detalhes da Venda
class SaleDetails(Base):
    __tablename__ = 'sale_details'
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey('sales.id'))
    total_paid = Column(Float)
    change = Column(Float)
    payment_methods = Column(String)  # Pode usar um formato JSON para armazenar formas de pagamento
    product_details = Column(String)  # Pode usar um formato JSON para armazenar detalhes dos produtos (ID e quantidades)
    sale = relationship("Sales", back_populates="sale_details")