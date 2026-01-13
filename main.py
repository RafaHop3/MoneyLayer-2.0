import os, yfinance as yf, pandas as pd, plotly.express as px
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

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

# CPF Limpo para comparação
YOUR_GOD_CPF = "86001396000"

@app.post("/dashboard", response_class=HTMLResponse)
async def dashboard(cpf: str = Form(...)):
    # Remove qualquer ponto, traço ou espaço enviado pelo navegador
    clean_cpf = "".join(filter(str.isdigit, cpf))
    
    db = SessionLocal()
    user = db.query(User).filter(User.cpf == clean_cpf).first()
    
    # Validação dupla: verifica o CPF fixo OU se o banco já marcou como GOD
    if clean_cpf != YOUR_GOD_CPF and (not user or not user.is_god):
        db.close()
        return "<h1>ACESSO NEGADO: Identidade não confirmada</h1>"
    
    # Se passou, garante que está no banco como GOD
    if user and not user.is_god and clean_cpf == YOUR_GOD_CPF:
        user.is_god = True
        db.commit()

    # (Restante do código do Dashboard com Plotly que enviamos antes...)
    tickers = ["AAPL", "TSLA", "PETR4.SA"]
    df = yf.download(tickers, period="1d", interval="15m")['Close']
    fig = px.line(df, title="Monitoramento Global de Mercado (Tempo Real)", template="plotly_dark")
    chart_html = fig.to_html(full_html=False)
    db.close()

    return f"""
    <html>
    <head>
        <style>
            body {{ margin:0; display:flex; background:#0a0a0a; color:white; font-family:sans-serif; }}
            .sidebar {{ width:260px; background:#111; height:100vh; padding:20px; border-right:1px solid #222; }}
            .content {{ flex:1; padding:40px; overflow-y:auto; }}
            .card {{ background:#161616; padding:20px; border-radius:10px; border-left:4px solid #ffd700; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2 style="color:#ffd700">MONEYLAYER GOD</h2>
            <p>Admin ID: 1</p>
            <hr>
            <p style="color:#2ecc71">ACESSO AUTORIZADO</p>
        </div>
        <div class="content">
            <h1>Intelligence Dashboard</h1>
            <div style="background:#111; padding:20px; border-radius:15px;">
                {chart_html}
            </div>
        </div>
    </body>
    </html>
    """
