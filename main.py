import os, random, yfinance as yf
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Configurações de Banco
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String, unique=True, index=True)
    is_admin = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)
app = FastAPI(title="MoneyLayer 2.0")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return """
    <html>
        <head>
            <title>MoneyLayer 2.0</title>
            <style>
                body { background: #000; color: #fff; font-family: sans-serif; text-align: center; padding-top: 50px; }
                .card { border: 1px solid #333; padding: 20px; display: inline-block; border-radius: 10px; }
                .btn-pay { background: #ffcc00; border: none; padding: 10px 20px; font-weight: bold; cursor: pointer; border-radius: 5px; }
                h1 { color: #ffcc00; }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>MONEYLAYER <span style="font-size: 0.5em; background: #333; padding: 4px; border-radius: 4px;">v2.0</span></h1>
                <p>INTERESSE SOCIAL E CONTROLE GLOBAL</p>
                <form action="/auth/identify" method="post">
                    <input type="text" name="cpf" placeholder="Digite seu CPF" style="padding: 10px; width: 80%; margin-bottom: 10px;"><br>
                    <button type="submit" class="btn-pay">VERIFICAR CAMADA</button>
                </form>
                <hr style="border-color: #222;">
                <button class="btn-pay" style="background: #222; color: #fff; margin-top: 10px;">EFETUAR PAGAMENTO</button>
                <p style="font-size: 10px; color: #555; margin-top: 20px;">THE ORBE SYSTEMS</p>
            </div>
        </body>
    </html>
    """

@app.post("/auth/identify")
async def identify(cpf: str = Form(...)):
    # Lógica de auditoria e interesse social aqui
    return {"status": "Identificado", "cpf": cpf, "msg": "Acesso à camada em processamento"}

@app.get("/health")
async def health():
    return {"status": "alive", "project": "MoneyLayer"}
