# backend/models/ledger.py
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

# Enums
class AccountType(str, Enum):
    USER = "user"
    SOCIAL_FUND = "social_fund"
    SYSTEM = "system"
    ESCROW = "escrow"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

# 1. Modelo de Contas (Atualizado com Auth)
class Account(SQLModel, table=True):
    __tablename__ = "accounts"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    
    # --- NOVOS CAMPOS DE SEGURANÇA ---
    # Username único para login (indexado para busca rápida)
    username: str = Field(index=True, unique=True) 
    # Senha criptografada (NUNCA salvar senha pura)
    hashed_password: str = Field()                 
    # ---------------------------------

    account_type: AccountType = Field(default=AccountType.USER)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relacionamento reverso
    entries: List["JournalEntry"] = Relationship(back_populates="account")

# 2. Modelo de Transações
class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    id: Optional[int] = Field(default=None, primary_key=True)
    reference: str = Field(unique=True, index=True) # UUID externo
    description: Optional[str] = None
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)
    audit_hash: Optional[str] = None # Governança
    created_at: datetime = Field(default_factory=datetime.utcnow)

    entries: List["JournalEntry"] = Relationship(back_populates="transaction")

# 3. Modelo de Entradas (O "Átomo" do Ledger)
class JournalEntry(SQLModel, table=True):
    __tablename__ = "journal_entries"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Chaves estrangeiras
    transaction_id: int = Field(foreign_key="transactions.id")
    account_id: int = Field(foreign_key="accounts.id")
    
    # Decimal é crucial para dinheiro
    amount: Decimal = Field(default=0, max_digits=14, decimal_places=2)

    # Relacionamentos
    transaction: Optional[Transaction] = Relationship(back_populates="entries")
    account: Optional[Account] = Relationship(back_populates="entries")