import os, yfinance as yf, plotly.express as px
from fastapi import FastAPI, Form, Request, HTTPException, Header
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

app = FastAPI()

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class GlobalValue(Base):
    __tablename__ = "global_values"
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)
    value = Column(Float)

Base.metadata.create_all(bind=engine)

GOD_CPF = "86001396000"
MASTER_API_KEY = os.getenv("MONEYLAYER_API_KEY", "padrao_seguro_123")

# ROTA DE COMANDO SOBERANO (API)
@app.patch("/governance/update")
async def update_social_index(value: float, x_api_key: str = Header(None)):
    if x_api_key != MASTER_API_KEY:
        raise HTTPException(status_code=403, detail="Chave API Inválida")
    
    db = SessionLocal()
    obj = db.query(GlobalValue).filter(GlobalValue.key == "social_multiplier").first()
    if not obj:
        obj = GlobalValue(key="social_multiplier", value=value)
        db.add(obj)
    else:
        obj.value = value
    db.commit()
    db.close()
    return {"status": "Global Value Updated", "new_multiplier": value}

@app.post("/dashboard", response_class=HTMLResponse)
async def dashboard(cpf: str = Form(...), input_code: str = Form(...)):
    db = SessionLocal()
    clean_cpf = "".join(filter(str.isdigit, cpf))
    is_admin = (clean_cpf == GOD_CPF)
    
    # Busca multiplicador global
    social_index = db.query(GlobalValue).filter(GlobalValue.key == "social_multiplier").first()
    idx_val = social_index.value if social_index else 1.0
    db.close()

    # Coleta e Ajuste de Mercado
    assets = ["USDBRL=X", "BTC-USD"]
    data = yf.download(assets, period="1d")['Close']
    dolar_social = data['USDBRL=X'].iloc[-1] * idx_val

    return f"""
    <body style="background:#000; color:#fff; font-family:sans-serif; padding:40px;">
        <h1 style="color:#ffd700">MONEYLAYER SOBERANO</h1>
        <div style="border:1px solid #333; padding:20px; border-radius:10px;">
            <h3>Dólar (Visão Social Ajustada):</h3>
            <p style="font-size:2em; color:#2ecc71;">R$ {dolar_social:.2f}</p>
            <p>Multiplicador Ativo: {idx_val}</p>
        </div>
        {"<p style='color:red;'>MODO GOD ATIVADO: Você tem permissão de escrita via API.</p>" if is_admin else ""}
    </body>
    """
