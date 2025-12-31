# backend/routers/transactions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from backend.database import get_session
from backend.services.transaction_service import TransactionService
from backend.schemas.transaction import TransactionCreate, TransactionRead

# Define o prefixo da URL: /api/v1/transactions
router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/", response_model=TransactionRead)
def create_transaction(
    tx_data: TransactionCreate, 
    session: Session = Depends(get_session)
):
    """
    Executa uma transferência financeira com aplicação automática de Taxa Social.
    """
    service = TransactionService(session)
    try:
        transaction = service.process_transaction(
            source_account_id=tx_data.source_account_id,
            target_account_id=tx_data.target_account_id,
            amount=tx_data.amount,
            description=tx_data.description,
            apply_social_tax=True # Sempre aplica a regra social na API pública
        )
        return transaction
    except ValueError as e:
        # Erros de negócio (ex: saldo negativo, valor inválido)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Erros genéricos de servidor
        print(f"Erro crítico: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no processamento da transação.")