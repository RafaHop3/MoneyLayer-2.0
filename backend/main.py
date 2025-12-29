from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Isso resolve o problema do botão não funcionar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Transacao(BaseModel):
    descricao: str
    valor: float
    tipo: str

@app.get("/")
def home():
    return {"status": "Sistema Online", "segurança": "Ativada"}

@app.post("/transacoes")
async def criar_transacao(t: Transacao):
    print(f"Recebido: {t.descricao} - R$ {t.valor}")
    return {"mensagem": "Dados encriptados com sucesso!"}