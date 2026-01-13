import os, yfinance as yf, plotly.express as px
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Database & Security
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
    # Inteligência de Mercado Real
    stocks = ["AAPL", "TSLA", "PETR4.SA", "ITUB4.SA"]
    df = yf.download(stocks, period="1mo", interval="1d")['Close']
    fig = px.line(df, title="Tendência Mensal de Ativos", template="plotly_dark")
    fig.update_layout(paper_bgcolor="#111", plot_bgcolor="#111", font_color="#ffd700")
    chart_html = fig.to_html(full_html=False)

    return f"""
    <html>
    <head>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ margin: 0; background: #050505; color: #eee; font-family: 'Inter', sans-serif; display: flex; height: 100vh; }}
            .sidebar {{ width: 280px; background: #0a0a0a; border-right: 1px solid #222; padding: 25px; }}
            .main {{ flex: 1; padding: 40px; overflow-y: auto; background: linear-gradient(135deg, #050505 0%, #111 100%); }}
            .nav-top {{ display: flex; gap: 30px; border-bottom: 2px solid #222; margin-bottom: 30px; }}
            .nav-item {{ padding: 15px 0; cursor: pointer; color: #666; font-weight: 600; text-transform: uppercase; transition: 0.3s; }}
            .nav-item.active {{ color: #ffd700; border-bottom: 2px solid #ffd700; }}
            .grid-tools {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
            .tool-card {{ background: #161616; border: 1px solid #333; padding: 25px; border-radius: 12px; transition: 0.3s; }}
            .tool-card:hover {{ border-color: #ffd700; transform: translateY(-5px); }}
            .badge {{ background: #ffd700; color: #000; padding: 4px 8px; border-radius: 4px; font-size: 0.7em; margin-left: 10px; }}
            .hidden {{ display: none; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2 style="color:#ffd700">MONEYLAYER <span style="font-weight:200">PRO</span></h2>
            <p style="color:#555; font-size:0.9em;">ID SOBERANO: 001</p>
            <div style="margin-top:40px;">
                <p style="color:#ffd700; font-size:0.75em; letter-spacing:1px;">SUB-SISTEMAS</p>
                <div class="nav-item active" onclick="showTab('empresa')">Gestão Business</div>
                <div class="nav-item" onclick="showTab('trabalhador')">Gestão Individual</div>
            </div>
        </div>
        <div class="main">
            <div id="sec-empresa" class="section">
                <h1>Hub de Inteligência Empresarial</h1>
                <div class="grid-tools">
                    <div class="tool-card">
                        <h3>Simulador Fiscal <span class="badge">PJ</span></h3>
                        <p>Compare Simples Nacional vs Lucro Presumido para otimizar sua margem.</p>
                        <button style="width:100%; padding:10px; background:#ffd700; border:0; cursor:pointer;">Calcular agora</button>
                    </div>
                    <div class="tool-card">
                        <h3>Monitor de Concorrência</h3>
                        <p>Acompanhe Petrobras e Vale em tempo real para insights de setor.</p>
                        {chart_html}
                    </div>
                </div>
            </div>
            <div id="sec-trabalhador" class="section hidden">
                <h1>Hub de Prosperidade do Trabalhador</h1>
                <div class="grid-tools">
                    <div class="tool-card" style="border-left: 5px solid #2ecc71;">
                        <h3>Calculadora de Liberdade</h3>
                        <p>Descubra quanto investir por mês para viver de renda em 10 anos.</p>
                    </div>
                    <div class="tool-card">
                        <h3>CLT vs PJ: O Veredito</h3>
                        <p>Insira seu salário e compare os benefícios reais após impostos.</p>
                    </div>
                </div>
            </div>
        </div>
        <script>
            function showTab(tab) {{
                document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
                document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
                if(tab === 'empresa') {{
                    document.getElementById('sec-empresa').classList.remove('hidden');
                    event.target.classList.add('active');
                }} else {{
                    document.getElementById('sec-trabalhador').classList.remove('hidden');
                    event.target.classList.add('active');
                }}
            }}
        </script>
    </body>
    </html>
    """
