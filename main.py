import os, yfinance as yf, pandas as pd, plotly.express as px
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    cpf = Column(String, unique=True)
    is_god = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

YOUR_GOD_CPF = "86001396000"

@app.get("/", response_class=HTMLResponse)
async def login_ui():
    return """
    <body style="background:#050505; color:white; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh;">
        <form action="/dashboard" method="post" style="background:#111; padding:40px; border-radius:15px; border:1px solid #ffd700; text-align:center;">
            <h1 style="color:#ffd700">GOD AUTH</h1>
            <input type="text" name="cpf" placeholder="DIGITE SEU CPF" required style="padding:10px; width:250px; background:#000; color:#ffd700; border:1px solid #333;"><br><br>
            <button type="submit" style="background:#ffd700; color:black; border:0; padding:10px 30px; cursor:pointer; font-weight:bold;">ENTRAR</button>
        </form>
    </body>
    """

@app.post("/dashboard", response_class=HTMLResponse)
async def dashboard(cpf: str = Form(...)):
    if cpf != YOUR_GOD_CPF:
        return "<h1>ACESSO NEGADO: Identidade não confirmada</h1>"
    
    # Busca de dados para o Gráfico
    tickers = ["AAPL", "TSLA", "PETR4.SA"]
    df = yf.download(tickers, period="1d", interval="15m")['Close']
    
    # Criar um gráfico simples em HTML usando Plotly
    fig = px.line(df, title="Monitoramento Global de Mercado (Tempo Real)", template="plotly_dark")
    chart_html = fig.to_html(full_html=False)

    return f"""
    <html>
    <head>
        <style>
            body {{ margin:0; display:flex; background:#0a0a0a; color:white; font-family:sans-serif; }}
            .sidebar {{ width:260px; background:#111; height:100vh; padding:20px; border-right:1px solid #222; }}
            .content {{ flex:1; padding:40px; overflow-y:auto; }}
            .tab-btn {{ display:block; width:100%; padding:15px; background:none; border:none; color:#888; text-align:left; cursor:pointer; font-size:16px; border-bottom:1px solid #222; }}
            .tab-btn:hover, .active {{ color:#ffd700; background:#1a1a1a; }}
            .stats-grid {{ display:grid; grid-template-columns: repeat(3, 1fr); gap:20px; margin-bottom:40px; }}
            .card {{ background:#161616; padding:20px; border-radius:10px; border-left:4px solid #ffd700; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2 style="color:#ffd700">MONEYLAYER GOD</h2>
            <p>Admin ID: 1</p>
            <button class="tab-btn active">Inteligência de Mercado</button>
            <button class="tab-btn">Segurança Cyber</button>
            <button class="tab-btn">Auditoria Social</button>
        </div>
        <div class="content">
            <h1>Intelligence Dashboard</h1>
            <div class="stats-grid">
                <div class="card"><h3>Apple Inc.</h3><p>Online</p></div>
                <div class="card"><h3>Tesla</h3><p>Online</p></div>
                <div class="card"><h3>Petrobras</h3><p>Online</p></div>
            </div>
            <div style="background:#111; padding:20px; border-radius:15px;">
                {chart_html}
            </div>
        </div>
    </body>
    </html>
    """
