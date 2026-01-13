import os, yfinance as yf, plotly.express as px
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

# O CPF fica numa variável interna que não é exibida na UI
GOD_KEY = "86001396000"

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <body style="background:#050505; color:white; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh;">
        <form action="/dashboard" method="post" style="background:#111; padding:40px; border-radius:15px; border:1px solid #333;">
            <h1 style="color:#ffd700">MONEYLAYER <span style="font-size:0.5em; color:#888;">v2.0</span></h1>
            <input type="password" name="cpf" placeholder="CHAVE DE ACESSO" required 
                   style="padding:12px; width:280px; background:#000; color:#ffd700; border:1px solid #444; border-radius:5px; text-align:center;"><br><br>
            <button type="submit" style="background:#ffd700; color:black; border:0; padding:12px 30px; cursor:pointer; font-weight:bold; width:100%;">AUTENTICAR</button>
        </form>
    </body>
    """

@app.post("/dashboard", response_class=HTMLResponse)
async def dashboard(cpf: str = Form(...)):
    # Limpa o input para garantir que espaços não quebrem o acesso
    clean_cpf = "".join(filter(str.isdigit, cpf))
    
    if clean_cpf != GOD_KEY:
        return "<body style='background:#000; color:red; text-align:center; padding-top:100px;'><h1>ACESSO NEGADO</h1><a href='/'>Voltar</a></body>"

    # Se for o GOD, o sistema gera o dashboard
    tickers = ["AAPL", "TSLA", "BTC-USD", "ETH-USD"]
    df = yf.download(tickers, period="1d", interval="15m")['Close']
    fig = px.line(df, title="Intelligence Stream - GOD MODE", template="plotly_dark")
    chart_html = fig.to_html(full_html=False)

    return f"""
    <html>
    <head>
        <style>
            body {{ margin:0; display:flex; background:#0a0a0a; color:white; font-family:sans-serif; }}
            .sidebar {{ width:260px; background:#111; height:100vh; padding:20px; border-right:1px solid #222; }}
            .content {{ flex:1; padding:40px; overflow-y:auto; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2 style="color:#ffd700">GOD CONSOLE</h2>
            <p style="color:#2ecc71">● SISTEMA OPERACIONAL</p>
            <hr style="border:0; border-top:1px solid #333;">
            <p style="font-size:0.8em; color:#666;">ID SOBERANO: 001</p>
        </div>
        <div class="content">
            {chart_html}
        </div>
    </body>
    </html>
    """
