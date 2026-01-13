import os, random, yfinance as yf
from fastapi import FastAPI, Form, Request, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional

# --- CONFIGURAÇÃO DE BANCO ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Conversion(Base):
    __tablename__ = "conversions"
    id = Column(Integer, primary_key=True, index=True)
    cpf_owner = Column(String, index=True)
    brl_value = Column(Float)
    lyr_value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_market_val():
    try:
        ticker = yf.Ticker("USDBRL=X")
        return round(ticker.history(period="1d")['Close'].iloc[-1], 2)
    except: return 5.40

@app.get("/", response_class=HTMLResponse)
async def index(cpf_session: Optional[str] = Cookie(None)):
    if not cpf_session:
        # TELA DE LOGIN (RESTAURADA E MELHORADA)
        return """
        <html>
            <head><title>MoneyLayer | Identify</title>
            <style>
                body { background: #000; color: #ffcc00; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                .login-card { background: #0a0a0a; padding: 40px; border-radius: 20px; border: 1px solid #222; text-align: center; width: 320px; }
                h1 { letter-spacing: 5px; margin-bottom: 10px; }
                input { background: #111; border: 1px solid #333; color: #fff; padding: 15px; width: 100%; border-radius: 8px; margin: 20px 0; text-align: center; }
                .btn { background: #ffcc00; color: #000; padding: 15px; width: 100%; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
                .footer { margin-top: 30px; font-size: 10px; color: #333; }
            </style></head>
            <body>
                <div class="login-card">
                    <h1>MONEYLAYER</h1>
                    <div style="font-size: 10px; color: #555;">IDENTIFICAÇÃO DE CAMADA SOCIAL</div>
                    <form action="/login" method="post">
                        <input type="text" name="cpf" placeholder="DIGITE SEU CPF" required>
                        <button type="submit" class="btn">ACESSAR SOBERANIA</button>
                    </form>
                    <div class="footer">THE ORBE SYSTEMS</div>
                </div>
            </body>
        </html>
        """
    
    # DASHBOARD (SÓ APARECE APÓS LOGIN)
    val = get_market_val()
    db = SessionLocal()
    history = db.query(Conversion).filter(Conversion.cpf_owner == cpf_session).order_by(Conversion.timestamp.desc()).limit(5).all()
    db.close()
    
    history_html = "".join([f"<div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #222; font-size:12px;'><span>{c.timestamp.strftime('%H:%M')}</span><span style='color:#00ff00;'>{c.lyr_value} LYR</span></div>" for c in history])

    return f"""
    <html>
        <head><title>Dashboard | MoneyLayer</title>
        <style>
            body {{ background: #050505; color: #eee; font-family: sans-serif; padding: 20px; }}
            .container {{ max-width: 400px; margin: auto; }}
            .card {{ background: #111; padding: 20px; border-radius: 15px; border: 1px solid #222; margin-bottom: 20px; }}
            .gold {{ color: #ffcc00; }}
            .btn {{ background: #ffcc00; color: #000; padding: 12px; width: 100%; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }}
            input {{ background: #1a1a1a; border: 1px solid #333; color: #fff; padding: 12px; width: 100%; border-radius: 8px; margin: 10px 0; box-sizing: border-box; }}
        </style></head>
        <body>
            <div class="container">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h2 class="gold">DASHBOARD</h2>
                    <a href="/logout" style="color:#555; font-size:12px; text-decoration:none;">Sair [x]</a>
                </div>
                <div class="card">
                    <div style="font-size:10px; color:#555;">CPF ATIVO: {cpf_session}</div>
                    <div style="font-size:11px; margin-top:10px;">REFERÊNCIA GLOBAL: <span class="gold">R$ {val}</span></div>
                </div>
                <div class="card">
                    <form action="/convert" method="post">
                        <input type="number" step="0.01" name="amount" placeholder="Valor para Conversão (BRL)" required>
                        <button type="submit" class="btn">REGISTRAR NA CAMADA</button>
                    </form>
                </div>
                <div class="card">
                    <div style="font-size:11px; color:#555; margin-bottom:10px;">SEU HISTÓRICO SOCIAL</div>
                    {history_html or "Aguardando primeiro registro..."}
                </div>
            </div>
        </body>
    </html>
    """

@app.post("/login")
async def login(cpf: str = Form(...)):
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="cpf_session", value=cpf)
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("cpf_session")
    return response

@app.post("/convert")
async def convert(amount: float = Form(...), cpf_session: str = Cookie(None)):
    if not cpf_session: return RedirectResponse(url="/", status_code=303)
    rate = get_market_val()
    lyr = round(amount / rate, 4)
    db = SessionLocal()
    db.add(Conversion(cpf_owner=cpf_session, brl_value=amount, lyr_value=lyr))
    db.commit()
    db.close()
    return RedirectResponse(url="/", status_code=303)
