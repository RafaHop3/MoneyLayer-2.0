import os, datetime, yfinance as yf
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Banco de Dados
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

@app.get("/", response_class=HTMLResponse)
async def login_page():
    return """
    <html>
    <head>
        <style>
            body { background: #0a0a0a; color: #fff; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .login-card { background: #1a1a1a; padding: 40px; border-radius: 15px; border: 1px solid #333; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
            input { background: #000; border: 1px solid #444; color: #ffd700; padding: 12px; border-radius: 5px; width: 250px; margin-bottom: 20px; outline: none; }
            button { background: #ffd700; color: #000; border: none; padding: 12px 30px; border-radius: 5px; cursor: pointer; font-weight: bold; transition: 0.3s; }
            button:hover { background: #fff; transform: translateY(-2px); }
        </style>
    </head>
    <body>
        <div class="login-card">
            <h1>MONEYLAYER <span style="color:#ffd700">2.0</span></h1>
            <form action="/dashboard" method="post">
                <input type="text" name="cpf" placeholder="IDENTIFICAÇÃO GOD" required><br>
                <button type="submit">ENTRAR NO SISTEMA</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/dashboard", response_class=HTMLResponse)
async def dashboard(cpf: str = Form(...)):
    if cpf != "86001396000":
        return "Acesso Negado"
    
    # Coleta de Dados de Empresas Diversificadas
    tickers = ["AAPL", "PETR4.SA", "VALE3.SA", "TSLA", "AMZN"]
    market_data = ""
    for t in tickers:
        stock = yf.Ticker(t)
        price = stock.fast_info['last_price']
        market_data += f"<div class='card'><h4>{t}</h4><p>Preço Atual: <span style='color:#2ecc71'>$ {price:.2f}</span></p></div>"

    return f"""
    <html>
    <head>
        <style>
            body {{ margin: 0; display: flex; background: #050505; color: white; font-family: sans-serif; }}
            .sidebar {{ width: 250px; background: #111; height: 100vh; border-right: 1px solid #333; padding: 20px; }}
            .main-content {{ flex: 1; padding: 30px; }}
            .tabs {{ display: flex; gap: 10px; margin-bottom: 30px; border-bottom: 1px solid #333; padding-bottom: 10px; }}
            .tab-btn {{ background: none; border: none; color: #888; cursor: pointer; font-size: 16px; padding: 10px; }}
            .tab-btn.active {{ color: #ffd700; border-bottom: 2px solid #ffd700; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }}
            .card {{ background: #1a1a1a; padding: 20px; border-radius: 10px; border: 1px solid #333; }}
            #intelligence, #security {{ display: none; }}
            .active-section {{ display: block !important; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2 style="color:#ffd700">GOD PANEL</h2>
            <p>ID: 1</p>
            <hr style="border-color:#222">
            <button class="tab-btn active" onclick="show('intelligence')">Inteligência de Mercado</button><br>
            <button class="tab-btn" onclick="show('security')">Segurança Sentinel</button>
        </div>
        <div class="main-content">
            <div id="intelligence" class="active-section">
                <h1>Global Market Analysis</h1>
                <div class="grid">{market_data}</div>
            </div>
            <div id="security">
                <h1>Sentinela de Acessos</h1>
                <p>Monitorando logs de intrusão e CPFs...</p>
                <div class="card" style="border-color: red;">Monitoramento em Tempo Real Ativo</div>
            </div>
        </div>
        <script>
            function show(id) {{
                document.getElementById('intelligence').classList.remove('active-section');
                document.getElementById('security').classList.remove('active-section');
                document.getElementById(id).classList.add('active-section');
            }}
        </script>
    </body>
    </html>
    """
