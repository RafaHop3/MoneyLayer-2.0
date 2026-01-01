from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from decimal import Decimal
from sqlalchemy.orm import Session
from typing import Dict, Any

from backend.database import get_db
from backend.core.models import Transaction
from backend.core.social_rules import calcular_distribuicao
from backend.core.money_safety import MoneySystemError

# O prefixo aqui se soma ao do main.py
# Resultado final: /api/v1/social
router = APIRouter(prefix="/social", tags=["Social Money Layer"])

class TransactionRequest(BaseModel):
    valor: Decimal
    description: str = "Transação Social Automática"
    user_id: int = 1

# Rota final: /api/v1/social/processar-distribuicao
@router.post("/processar-distribuicao")
async def execute_social_distribution(
    request: TransactionRequest, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    try:
        # 1. Calcula
        resultado = calcular_distribuicao(request.valor)
        
        # 2. Prepara
        nova_transacao = Transaction(
            amount=request.valor,
            description=request.description,
            owner_id=request.user_id,
            social_tax_rate=resultado['taxa_aplicada'],
            social_value=resultado['social'],
            net_value=resultado['destino'],
            is_social_audited=True
        )

        # 3. Salva
        db.add(nova_transacao)
        db.commit()
        db.refresh(nova_transacao)

        return {
            "status": "success",
            "mensagem": "Transação processada e salva no Ledger.",
            "db_id": nova_transacao.id,
            "auditoria": {
                "entrada": float(nova_transacao.amount),
                "fundo_social": float(nova_transacao.social_value),
                "destino_final": float(nova_transacao.net_value)
            }
        }
    
    except MoneySystemError as e:
        raise HTTPException(status_code=400, detail=f"BLOQUEIO: {str(e)}")
    except Exception as e:
        print(f"Erro DB: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor.")
