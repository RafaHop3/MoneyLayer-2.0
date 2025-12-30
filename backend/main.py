from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import transacoes  # Importando nosso novo arquivo de rotas

app = FastAPI()

# Configuração de CORS (Permite que o Frontend fale com a gente)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conectando as rotas
app.include_router(transacoes.router)

@app.get("/")
def home():
    return {"status": "MoneyLayer 2.0 - Arquitetura Limpa"}