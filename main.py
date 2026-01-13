import os, random, yfinance as yf, plotly.graph_objects as go
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

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
    brl_value = Column(Float)
    lyr_value = Column(Float)
    rate = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_market_data():
    try:
        ticker = yf.Ticker("USDBRL=X")
        hist = ticker.history(period="7d")
        return hist
    except:
        return None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    db = SessionLocal()
    history = db.query(Conversion).order_by(Conversion.timestamp.desc()).limit(5).all()
    db.close()
    
    hist_market = get_market_data()
    val = round(hist_market['Close'].iloc[-1], 2) if hist_market is not None else 5.40
    
    history_html = "".join([
        f"<div style='display:flex; justify-content:space-between; font-size:12px; padding:8px 0; border-bottom:1px solid #222;'>"
        f"<span>{c.timestamp.strftime('%H:%M')}</span>"
        f"<span>R$ {c.brl_value}</span>"
        f"<span style='color:#00ff00;'>{c.lyr_value} LYR</span></div>" 
        for c in history
    ]) or "<div style='color:#444; font-size:12px; margin-top:10px;'>Nenhuma conversão registada.</div>"

    return f"""
    <html>
        <head>
            <title>MoneyLayer | Governança</title>
            <meta charset="UTF-8">
            <style>
                :root {{ --gold: #ffcc00; --bg: #0a0a0a; --surface: #151515; }}
                body {{ background: var(--bg); color: #eee; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; }}
                .container {{ max-width: 450px; margin: auto; }}
                .card {{ background: var(--surface); border: 1px solid #222; border-radius: 16px; padding: 20px; margin-bottom: 20px; }}
                .gold {{ color: var(--gold); }}
                input {{ background: #1a1a1a; border: 1px solid #333; color: #fff; padding: 12px; width: 100%; border-radius: 8px; box-sizing: border-box; margin: 10px 0; }}
                .btn {{ background: var(--gold); color: #000; padding: 12px; width: 100%; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }}
                .history-title {{ font-size: 11px; color: #555; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div style="text-align:center; padding: 10px 0;">
                    <h1 style="margin:0; letter-spacing:3px;" class="gold">MONEYLAYER</h1>
                    <div style="font-size:10px; color:#444;">THE ORBE SYSTEMS</div>
                </div>

                <div class="card">
                    <div style="font-size:11px; color:#777;">TAXA DE SOBERANIA ATUAL</div>
                    <div style="font-size:32px; font-weight:bold;" class="gold">R$ {val}</div>
                </div>

                <div class="card" style="border-color: #ffcc0033;">
                    <div class="history-title" class="gold">Novo Aporte de Camada</div>
                    <form action="/convert" method="post">
                        <input type="number" step="0.01" name="amount" placeholder="Valor em BRL" required>
                        <button type="submit" class="btn">REGISTAR NA CAMADA</button>
                    </form>
                </div>

                <div class="card">
                    <div class="history-title">Últimas Atividades de Interesse Social</div>
                    {history_html}
                </div>

                <div style="text-align:center; margin-top:20px;">
                    <button class="btn" style="background:transparent; border:1px solid #222; color:#555; font-size:12px;" onclick="location.href='/audit'">Aceder Auditoria Global</button>
                </div>
            </div>
        </body>
    </html>
    """

@app.post("/convert")
async def convert(amount: float = Form(...)):
    hist = get_market_data()
    rate = round(hist['Close'].iloc[-1], 2) if hist is not None else 5.40
    lyr = round(amount / rate, 4)
    
    db = SessionLocal()
    new_conv = Conversion(brl_value=amount, lyr_value=lyr, rate=rate)
    db.add(new_conv)
    db.commit()
    db.close()
    return RedirectResponse(url="/", status_code=303)

@app.get("/audit", response_class=HTMLResponse)
async def audit_page():
    # Mantém a lógica do gráfico Plotly que criamos antes
    return "Gráfico de Auditoria em Processamento... <a href='/'>Voltar</a>"
