from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

# Importa a dependência correta (get_db)
from backend.database import get_db
from backend.core.models import Transaction

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.get("/")
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).offset(skip).limit(limit).all()
    return transactions
