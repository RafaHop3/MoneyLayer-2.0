import os, yfinance as yf, plotly.express as px
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Database & Security Setup
DATABASE_URL = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    cpf = Column(String, unique=True)
    is_god = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

@app.post("/dashboard", response_class=HTMLResponse)
async def dashboard(cpf: str = Form(...), input_code: str = Form(...)):
    # Inteligência de Mercado: Moedas e Ações
    assets = ["USDBRL=X", "BTC-USD", "ETH-USD", "PETR4.SA", "AAPL"]
    data = yf.download(assets, period="5d", interval="1h")['Close']
    
    # Criando gráfico de performance comparativa
    fig = px.line(data, title="Fluxo Global de Ativos (5 Dias)", template="plotly_dark")
    fig.update_layout(paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a", font_color="#ffd700")
    chart_html = fig.to_html(full_html=False)

    return f"""
    <html>
    <head>
        <style>
            body {{ margin: 0; background: #050505; color: #fff; font-family: 'Inter', sans-serif; display: flex; height: 100vh; }}
            .sidebar {{ width: 280px; background: #000; border-right: 1px solid #222; padding: 25px; }}
            .main {{ flex: 1; padding: 40px; overflow-y: auto; }}
            .nav-item {{ padding: 12px; cursor: pointer; color: #888; transition: 0.3s; border-radius: 8px; margin-bottom: 5px; }}
            .nav-item:hover, .active {{ background: #1a1a1a; color: #ffd700; }}
            .card {{ background: #111; border: 1px solid #222; padding: 20px; border-radius: 12px; margin-bottom: 20px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
            .hidden {{ display: none; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2 style="color:#ffd700">MONEYLAYER <span style="font-weight:200">2.0</span></h2>
            <div style="margin-top:30px;">
                <div class="nav-item active" onclick="tab('market')">Inteligência Global</div>
                <div class="nav-item" onclick="tab('business')">Gestão Business</div>
                <div class="nav-item" onclick="tab('worker')">Gestão Individual</div>
            </div>
        </div>
        <div class="main">
            <div id="market" class="section">
                <h1>Monitor de Ativos Soberanos</h1>
                <div class="grid">
                    <div class="card"><h4>Dólar (BRL)</h4><p style="color:#2ecc71; font-size:1.5em;">R$ {data['USDBRL=X'].iloc[-1]:.2f}</p></div>
                    <div class="card"><h4>Bitcoin</h4><p style="color:#f1c40f; font-size:1.5em;">$ {data['BTC-USD'].iloc[-1]:.0f}</p></div>
                </div>
                <div class="card">{chart_html}</div>
            </div>
            
            <div id="business" class="section hidden">
                <h1>Painel da Empresa</h1>
                <div class="card"><h3>Análise de Capital de Giro</h3><p>Configure seus custos fixos para calcular o ROI social.</p></div>
            </div>

            <div id="worker" class="section hidden">
                <h1>Painel do Trabalhador</h1>
                <div class="card"><h3>Plano de Liberdade</h3><p>Calculando juros compostos para o CPF {cpf}...</p></div>
            </div>
        </div>
        <script>
            function tab(id) {{
                document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
                document.getElementById(id).classList.remove('hidden');
                document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
                event.target.classList.add('active');
            }}
        </script>
    </body>
    </html>
    """
