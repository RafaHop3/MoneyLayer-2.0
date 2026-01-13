import os, yfinance as yf, plotly.express as px
from fastapi import FastAPI, Form, Request
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
    updated_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    cpf = Column(String, unique=True)
    is_god = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

GOD_CPF = "86001396000"

@app.post("/dashboard", response_class=HTMLResponse)
async def dashboard(cpf: str = Form(...), input_code: str = Form(...)):
    db = SessionLocal()
    clean_cpf = "".join(filter(str.isdigit, cpf))
    is_admin = (clean_cpf == GOD_CPF)
    
    # Busca de Valor Global de Interesse Social (Default 1.0 se não existir)
    social_index = db.query(GlobalValue).filter(GlobalValue.key == "social_multiplier").first()
    idx_val = social_index.value if social_index else 1.0

    # Inteligência de Mercado
    assets = ["USDBRL=X", "BTC-USD"]
    data = yf.download(assets, period="5d", interval="1h")['Close']
    
    # Simulação Avançada: Otimização baseada no Índice Soberano
    dolar_ajustado = data['USDBRL=X'].iloc[-1] * idx_val

    db.close()

    return f"""
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
        <style>
            body {{ margin: 0; background: #050505; color: #fff; font-family: 'Inter', sans-serif; display: flex; height: 100vh; }}
            .sidebar {{ width: 280px; background: #000; border-right: 1px solid #222; padding: 25px; }}
            .main {{ flex: 1; padding: 40px; overflow-y: auto; }}
            .card {{ background: #111; border: 1px solid #222; padding: 20px; border-radius: 12px; margin-bottom: 20px; }}
            .admin-box {{ border: 1px solid #ffd700; padding: 20px; border-radius: 10px; background: #1a1a00; }}
            .btn-action {{ background: #ffd700; color: #000; border:0; padding:12px; border-radius:5px; font-weight:bold; cursor:pointer; width:100%; }}
            .nav-item {{ padding: 12px; cursor: pointer; color: #888; border-radius: 8px; margin-bottom: 5px; }}
            .active {{ background: #1a1a1a; color: #ffd700; }}
            .hidden {{ display: none; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2 style="color:#ffd700">MONEYLAYER <span style="font-weight:200">3.0</span></h2>
            <div class="nav-item active" onclick="tab('market')">Mercado Global</div>
            <div class="nav-item" onclick="tab('sim')">Simulação Avançada</div>
            {"<div class='nav-item' onclick='tab(\"god\")'>👑 GOVERNAÇÃO</div>" if is_admin else ""}
        </div>
        <div class="main">
            <div id="market" class="section">
                <h1>Visão Soberana</h1>
                <div class="card">
                    <h3>Dólar Ajustado (Índice Social: {idx_val}):</h3>
                    <p style="color:#2ecc71; font-size:2em;">R$ {dolar_ajustado:.2f}</p>
                </div>
            </div>

            <div id="sim" class="section hidden">
                <h1>Simulador de Investimento IA</h1>
                <div class="card">
                    <h3>Recomendação Baseada no seu Perfil:</h3>
                    <p id="ia-advice">Analisando tendências globais...</p>
                    <button class="btn-action" onclick="runIA()">Gerar Recomendação</button>
                </div>
            </div>

            <div id="god" class="section hidden">
                <h1>Painel de Controle de Valores Globais</h1>
                <div class="admin-box">
                    <label>Definir Multiplicador de Social (Global):</label>
                    <input type="number" step="0.1" id="new_idx" style="width:100%; margin:10px 0; padding:10px;">
                    <button class="btn-action" onclick="updateGlobal()">Atualizar Mundo</button>
                </div>
            </div>
        </div>
        <script>
            function tab(id) {{
                document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
                document.getElementById(id).classList.remove('hidden');
                document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
                event.target.classList.add('active');
            }}
            function runIA() {{
                const advice = ["Invista 20% em BTC para soberania.", "O Dólar está em zona de compra social.", "Aumente a liquidez da sua empresa hoje."];
                document.getElementById('ia-advice').innerHTML = "<b>Sugestão IA:</b> " + advice[Math.floor(Math.random()*advice.length)];
            }}
            async function updateGlobal() {{
                alert("Valor Global Atualizado. Todos os dashboards refletirão este índice.");
                // Aqui conectaríamos a rota de update do banco
            }}
        </script>
    </body>
    </html>
    """
