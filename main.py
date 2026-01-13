import os, yfinance as yf, plotly.express as px
from fastapi import FastAPI, Form, Request, HTTPException, Header
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

Base.metadata.create_all(bind=engine)

GOD_CPF = "86001396000"
MASTER_API_KEY = os.getenv("MONEYLAYER_API_KEY", "padrao_seguro_123")

@app.get("/", response_class=HTMLResponse)
async def login_page():
    return """
    <body style="background:#050505; color:white; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <form action="/dashboard" method="post" style="background:#111; padding:40px; border-radius:15px; border:1px solid #ffd700; text-align:center; box-shadow: 0 0 30px rgba(255,215,0,0.1);">
            <h1 style="color:#ffd700; letter-spacing:3px;">MONEYLAYER 3.0</h1>
            <p style="color:#666;">AUTENTICAÇÃO SOBERANA</p>
            <input type="password" name="cpf" placeholder="DIGITE SEU CPF" required style="padding:15px; width:280px; background:#000; color:#ffd700; border:1px solid #333; border-radius:5px; text-align:center;"><br><br>
            <input type="hidden" name="input_code" value="bypass">
            <button type="submit" style="background:#ffd700; color:black; border:0; padding:15px 30px; cursor:pointer; font-weight:bold; width:100%; border-radius:5px;">ACESSAR SISTEMA</button>
        </form>
    </body>
    """

@app.post("/dashboard", response_class=HTMLResponse)
async def dashboard(cpf: str = Form(...), input_code: str = Form(...)):
    db = SessionLocal()
    clean_cpf = "".join(filter(str.isdigit, cpf))
    is_admin = (clean_cpf == GOD_CPF)
    
    # Busca multiplicador global
    social_index = db.query(GlobalValue).filter(GlobalValue.key == "social_multiplier").first()
    idx_val = social_index.value if social_index else 1.0
    db.close()

    # Coleta de Mercado e Gráfico
    assets = ["USDBRL=X", "BTC-USD", "ETH-USD"]
    data = yf.download(assets, period="5d", interval="1h")['Close']
    
    # Cálculo Social
    dolar_real = data['USDBRL=X'].iloc[-1]
    dolar_social = dolar_real * idx_val
    
    fig = px.line(data, title="Fluxo de Mercado (Visão Soberana)", template="plotly_dark")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#ffd700")
    chart_html = fig.to_html(full_html=False)

    return f"""
    <html>
    <head>
        <style>
            body {{ margin: 0; background: #050505; color: #fff; font-family: 'Inter', sans-serif; display: flex; height: 100vh; overflow: hidden; }}
            .sidebar {{ width: 280px; background: #000; border-right: 1px solid #222; padding: 25px; display: flex; flex-direction: column; }}
            .main {{ flex: 1; padding: 40px; overflow-y: auto; background: radial-gradient(circle at top right, #111, #050505); }}
            .card {{ background: #111; border: 1px solid #222; padding: 25px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
            .nav-item {{ padding: 15px; cursor: pointer; color: #888; border-radius: 8px; margin-bottom: 8px; transition: 0.3s; }}
            .nav-item:hover, .active {{ background: #1a1a1a; color: #ffd700; border-left: 4px solid #ffd700; }}
            .stat-val {{ font-size: 2.5em; font-weight: bold; color: #2ecc71; margin: 10px 0; }}
            .hidden {{ display: none; }}
            .admin-tag {{ background: #ffd700; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 0.7em; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2 style="color:#ffd700; letter-spacing:2px;">MONEYLAYER</h2>
            <p style="font-size: 0.8em; color:#555;">ID: {"GOD-001" if is_admin else "USER-STD"}</p>
            <hr style="border:0; border-top:1px solid #222; margin: 20px 0;">
            <div class="nav-item active" onclick="tab('market')">Mercado Global</div>
            {"<div class='nav-item' onclick='tab(\"governance\")'>👑 Governação</div>" if is_admin else ""}
            <div class="nav-item" onclick="location.href='/'">Sair</div>
        </div>
        <div class="main">
            <div id="market" class="section">
                <h1>Painel de Inteligência</h1>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div class="card">
                        <small style="color:#888;">DÓLAR COMERCIAL</small>
                        <div class="stat-val">R$ {dolar_real:.2f}</div>
                    </div>
                    <div class="card">
                        <small style="color:#ffd700;">DÓLAR (VISÃO SOCIAL {idx_val}x)</small>
                        <div class="stat-val" style="color:#ffd700;">R$ {dolar_social:.2f}</div>
                    </div>
                </div>
                <div class="card">{chart_html}</div>
            </div>

            <div id="governance" class="section hidden">
                <h1>Comando de Governação {"<span class='admin-tag'>GOD MODE</span>" if is_admin else ""}</h1>
                <div class="card">
                    <h3>Ajustar Multiplicador Global de Interesse Social</h3>
                    <p style="color:#888;">Este valor altera a percepção de todos os usuários do sistema.</p>
                    <input type="number" step="0.01" id="val_input" value="{idx_val}" style="background:#000; color:#ffd700; border:1px solid #444; padding:15px; width:200px; border-radius:5px; font-size:1.2em;">
                    <button onclick="updateValue()" style="background:#ffd700; color:black; border:0; padding:15px 30px; border-radius:5px; font-weight:bold; cursor:pointer; margin-left:10px;">ATUALIZAR MUNDO</button>
                </div>
            </div>
        </div>
        <script>
            function tab(id) {{
                document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
                document.getElementById(id).classList.remove('hidden');
                document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
                event.currentTarget.classList.add('active');
            }}
            async function updateValue() {{
                const val = document.getElementById('val_input').value;
                const key = "{MASTER_API_KEY}";
                const response = await fetch('/governance/update?value=' + val, {{
                    method: 'PATCH',
                    headers: {{ 'x-api-key': key }}
                }});
                if(response.ok) {{
                    alert('Soberania confirmada: Valor Global Alterado!');
                    location.reload();
                }} else {{
                    alert('Erro na Governação. Verifique a Chave API.');
                }}
            }}
        </script>
    </body>
    </html>
    """

# ROTA DE API (PATCH) mantida para controle via terminal também
@app.patch("/governance/update")
async def update_social_index(value: float, x_api_key: str = Header(None)):
    if x_api_key != MASTER_API_KEY:
        raise HTTPException(status_code=403, detail="Chave API Inválida")
    db = SessionLocal()
    obj = db.query(GlobalValue).filter(GlobalValue.key == "social_multiplier").first()
    if not obj:
        obj = GlobalValue(key="social_multiplier", value=value)
        db.add(obj)
    else:
        obj.value = value
    db.commit()
    db.close()
    return {"status": "success", "new_value": value}
