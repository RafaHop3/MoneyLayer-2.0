import os, random, yfinance as yf, plotly.graph_objects as go
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- CONFIGURAÇÃO DE BANCO ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String, unique=True, index=True)

try:
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS cpf VARCHAR(14) UNIQUE;"))
        conn.commit()
except: pass

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
    hist = get_market_data()
    val = round(hist['Close'].iloc[-1], 2) if hist is not None else "5.40"
    return f"""
    <html>
        <head>
            <title>MoneyLayer | Sovereignty</title>
            <style>
                :root {{ --gold: #ffcc00; --bg: #050505; }}
                body {{ background: var(--bg); color: #fff; font-family: 'Inter', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
                .card {{ background: #111; border: 1px solid #222; padding: 40px; border-radius: 20px; text-align: center; width: 350px; border-top: 4px solid var(--gold); }}
                h1 {{ color: var(--gold); letter-spacing: 3px; text-transform: uppercase; margin-bottom: 0; }}
                .val {{ font-size: 32px; font-weight: bold; margin: 20px 0; color: #fff; }}
                input {{ background: #1a1a1a; border: 1px solid #333; color: var(--gold); padding: 15px; width: 100%; border-radius: 8px; margin-bottom: 10px; box-sizing: border-box; text-align: center; }}
                .btn {{ background: var(--gold); color: #000; padding: 15px; width: 100%; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; text-transform: uppercase; }}
                .btn-audit {{ background: transparent; color: #666; border: none; margin-top: 20px; cursor: pointer; text-decoration: underline; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>MoneyLayer</h1>
                <div style="font-size: 10px; color: #444; letter-spacing: 2px;">THE ORBE SYSTEMS</div>
                <div class="val">R$ {val}</div>
                <form action="/auth/identify" method="post">
                    <input type="text" name="cpf" placeholder="SEU CPF" required>
                    <button type="submit" class="btn">Validar Camada</button>
                </form>
                <button class="btn-audit" onclick="location.href='/audit'">Visualizar Auditoria de Valores Globais</button>
            </div>
        </body>
    </html>
    """

@app.get("/audit", response_class=HTMLResponse)
async def audit_page():
    hist = get_market_data()
    if hist is None: return "Erro ao carregar dados."
    
    fig = go.Figure(data=go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#ffcc00', width=3)))
    fig.update_layout(
        title="Auditoria de Valores Globais (7 Dias)",
        paper_bgcolor='#050505', plot_bgcolor='#050505',
        font=dict(color='#fff'),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#222')
    )
    
    chart_html = fig.to_html(full_html=False)
    
    return f"""
    <html>
        <head><title>Auditoria | MoneyLayer</title></head>
        <body style="background:#050505; color:#fff; font-family:sans-serif; padding: 20px;">
            <a href="/" style="color:#ffcc00; text-decoration:none;">← Voltar ao Painel</a>
            <div style="margin-top: 30px; background:#111; padding: 20px; border-radius: 15px; border: 1px solid #222;">
                {chart_html}
            </div>
            <div style="text-align:center; margin-top: 20px; color:#444; font-size: 12px;">
                RELATÓRIO DE INTERESSE SOCIAL GERADO PELA THE ORBE SYSTEMS
            </div>
        </body>
    </html>
    """

@app.post("/auth/identify")
async def identify(cpf: str = Form(...)):
    return {{"status": "Sincronizado", "cpf": cpf, "msg": "Governação Ativa"}}
