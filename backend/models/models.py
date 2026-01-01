from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

# --- CORREÇÃO AQUI ---
# Antes estava "from .database", mas o arquivo está na pasta pai.
from backend.database import Base
# ---------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # Relacionamento: Um usuário tem várias transações
    transactions = relationship("Transaction", back_populates="owner")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Campos Padrão (Legado)
    amount = Column(Numeric(10, 2), nullable=False) # Valor Total da Transação
    description = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # --- MONEY LAYER 2.0 (Campos Novos) ---
    social_tax_rate = Column(Numeric(5, 4), default=0) 
    social_value = Column(Numeric(10, 2), default=0)
    net_value = Column(Numeric(10, 2), default=0)
    is_social_audited = Column(Boolean, default=False)
    # --------------------------------------

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="transactions")
    