import os, yfinance as yf, plotly.express as px
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Database Setup
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
    # Inteligência de Mercado
    assets = ["USDBRL=X", "EURBRL=X", "BTC-USD", "PETR4.SA"]
    data = yf.download(assets, period="5d", interval="1h")['Close']
    
    dolar = data['USDBRL=X'].iloc[-1]
    euro = data['EURBRL=X'].iloc[-1]
    
    fig = px.line(data, title="Fluxo de Moedas e Ativos (Tempo Real)", template="plotly_dark")
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
            .input-box {{ background:#000; border:1px solid #333; color:#ffd700; padding:10px; border-radius:5px; width:100%; margin-top:10px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
            .hidden {{ display: none; }}
            button {{ background:#ffd700; color:#000; border:0; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer; margin-top:10px; width:100%; }}
            .result-box {{ margin-top:20px; padding:15px; border-radius:8px; background:#1a1a1a; border-left: 4px solid #ffd700; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2 style="color:#ffd700">MONEYLAYER <span style="font-weight:200">2.0</span></h2>
            <div style="margin-top:30px;">
                <div class="nav-item active" onclick="tab('market')">Mercado Global</div>
                <div class="nav-item" onclick="tab('tax')">Gestão Business (PJ)</div>
                <div class="nav-item" onclick="tab('worker')">Gestão Individual (CLT)</div>
            </div>
        </div>
        <div class="main">
            <div id="market" class="section">
                <h1>Painel de Câmbio</h1>
                <div class="grid">
                    <div class="card"><h4>Dólar Comercial</h4><p style="color:#2ecc71; font-size:1.5em;">R$ {dolar:.2f}</p></div>
                    <div class="card"><h4>Euro</h4><p style="color:#3498db; font-size:1.5em;">R$ {euro:.2f}</p></div>
                </div>
                <div class="card">{chart_html}</div>
            </div>
            
            <div id="tax" class="section hidden">
                <h1>Simulador Fiscal Business</h1>
                <div class="card" style="max-width:400px;">
                    <label>Faturamento Mensal (R$):</label>
                    <input type="number" id="faturamento" class="input-box" placeholder="Ex: 20000">
                    <label>Pró-labore (R$):</label>
                    <input type="number" id="folha" class="input-box" placeholder="Ex: 6000">
                    <button onclick="calcularFiscal()">Analisar Regime</button>
                    <div id="resultado-fiscal" class="result-box" style="display:none;"></div>
                </div>
            </div>

            <div id="worker" class="section hidden">
                <h1>Calculadora CLT vs PJ</h1>
                <div class="card" style="max-width:400px;">
                    <label>Proposta Salarial Bruta (R$):</label>
                    <input type="number" id="salario" class="input-box" placeholder="Ex: 8000">
                    <button onclick="calcularCLT()">Comparar Modelos</button>
                    <div id="resultado-clt" class="result-box" style="display:none;"></div>
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

            function calcularFiscal() {{
                let fat = document.getElementById('faturamento').value;
                let folha = document.getElementById('folha').value;
                let res = document.getElementById('resultado-fiscal');
                let fatorR = folha / fat;
                res.style.display = 'block';
                if (fatorR >= 0.28) {{
                    res.innerHTML = "✅ Simples Nacional (Anexo III): Fator R otimizado. Imposto reduzido para ~6%.";
                }} else {{
                    res.innerHTML = "⚠️ Alerta: Imposto de 15,5% detectado. Sugerimos aumentar Pró-labore para atingir Fator R.";
                }}
            }}

            function calcularCLT() {{
                let sal = parseFloat(document.getElementById('salario').value);
                let res = document.getElementById('resultado-clt');
                let liquidoCLT = sal * 0.85; // Simulação simples de INSS/IRRF
                let equivalentePJ = sal * 1.30; // Para compensar férias, 13º e FGTS
                res.style.display = 'block';
                res.innerHTML = "📊 <b>Resultado:</b><br>Líquido estimado (CLT): R$ " + liquidoCLT.toFixed(2) + 
                                "<br><br>Para valer a pena como <b>PJ</b>, sua nota fiscal deve ser de no mínimo: <b>R$ " + equivalentePJ.toFixed(2) + "</b>";
            }}
        </script>
    </body>
    </html>
    """
