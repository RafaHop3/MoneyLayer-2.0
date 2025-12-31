# backend/main.py
from fastapi import FastAPI
from backend.routers import transactions, auth # <--- Adicione auth

app = FastAPI(title="MoneyLayer 2.0 API", version="2.0.0")

app.include_router(auth.router, prefix="/api/v1")         # <--- Rota de Login
app.include_router(transactions.router, prefix="/api/v1") # Rota de Transações

@app.get("/")
def read_root():
    return {"message": "MoneyLayer 2.0 - Secure Mode 🔒"}