# backend/schemas/transaction.py
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
from datetime import datetime
from backend.models.ledger import TransactionStatus

# O que o usuário envia para criar uma transação
class TransactionCreate(BaseModel):
    source_account_id: int
    target_account_id: int
    amount: Decimal
    description: str

# O que a API devolve como resposta
class TransactionRead(BaseModel):
    id: int
    reference: str
    status: TransactionStatus
    audit_hash: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True # Permite ler direto do objeto do banco