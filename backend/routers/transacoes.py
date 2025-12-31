# backend/routers/transactions.py
# ... imports anteriores ...
from backend.auth_deps import get_current_user # <--- Importe o porteiro
from backend.models.ledger import Account      # <--- Importe o modelo

# ... (código do router) ...

@router.post("/", response_model=TransactionRead)
def create_transaction(
    tx_data: TransactionCreate, 
    session: Session = Depends(get_session),
    current_user: Account = Depends(get_current_user) # <--- A MÁGICA É AQUI!
):
    """
    Agora exige token! 'current_user' é a pessoa logada.
    """
    # (Opcional) Podemos forçar que a origem (source_id) seja o próprio usuário logado
    # if tx_data.source_account_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="Você só pode mover seu próprio dinheiro.")

    service = TransactionService(session)
    # ... o resto do código continua igual ...