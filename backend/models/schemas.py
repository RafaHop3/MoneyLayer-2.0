from sqlmodel import SQLModel, Field
from typing import Optional

class Transacao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    descricao: str
    valor: float
    tipo: str  # 'receita' ou 'despesa'
    
    # --- NOVOS CAMPOS PARA O OBJETIVO SOCIAL ---
    
    # 1. Para o Score Social
    categoria: str = Field(default="Geral") 
    impacto_score: int = Field(default=50) # De 0 (Nocivo) a 100 (Regenerativo)
    
    # 2. Para o Dízimo/Redistribuição
    taxa_social: float = Field(default=0.0) # Quanto foi doado nessa transação
    
    # 3. Para Transparência Radical
    is_public: bool = Field(default=False) # Se True, qualquer um pode ver (anonimizado)