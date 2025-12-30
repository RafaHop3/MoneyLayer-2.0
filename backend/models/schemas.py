# Arquivo: backend/models/schemas.py
from pydantic import BaseModel

class Transacao(BaseModel):
    descricao: str
    valor: float
    tipo: str