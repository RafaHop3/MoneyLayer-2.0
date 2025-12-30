from fastapi import APIRouter
from models.schemas import Transacao

router = APIRouter()

@router.post("/transacoes")
async def criar_transacao(t: Transacao):
    # Aqui a gente simula o processamento
    print(f"Processando no Router: {t.descricao} - R$ {t.valor}")
    return {"mensagem": "Sucesso! Rota separada no arquivo transacoes.py"}