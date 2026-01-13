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
    assets = ["USDBRL=X", "BTC-USD", "PETR4.SA"]
    data = yf.download(assets, period="5d", interval="1h")['Close']
    fig = px.line(data, title="Fluxo de Mercado Soberano", template="plotly_dark")
    fig.update_layout(paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a", font_color="#ffd700")
    chart_html = fig.to_html(full_html=False)

    return f"""
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
        <style>
            body {{ margin: 0; background: #050505; color: #fff; font-family: 'Inter', sans-serif; display: flex; height: 100vh; }}
            .sidebar {{ width: 280px; background: #000; border-right: 1px solid #222; padding: 25px; }}
            .main {{ flex: 1; padding: 40px; overflow-y: auto; }}
            .nav-item {{ padding: 12px; cursor: pointer; color: #888; border-radius: 8px; margin-bottom: 5px; }}
            .active {{ background: #1a1a1a; color: #ffd700; }}
            .card {{ background: #111; border: 1px solid #222; padding: 20px; border-radius: 12px; margin-bottom: 20px; }}
            .input-box {{ background:#000; border:1px solid #333; color:#ffd700; padding:10px; border-radius:5px; width:100%; margin-top:10px; }}
            button {{ background:#ffd700; color:#000; border:0; padding:12px; border-radius:5px; font-weight:bold; cursor:pointer; margin-top:10px; width:100%; }}
            .btn-pdf {{ background: #e74c3c; color: white; margin-top: 20px; }}
            .hidden {{ display: none; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2 style="color:#ffd700">MONEYLAYER <span style="font-weight:200">2.0</span></h2>
            <div style="margin-top:30px;">
                <div class="nav-item active" onclick="tab('market')">Mercado Global</div>
                <div class="nav-item" onclick="tab('tax')">Gestão Business</div>
                <div class="nav-item" onclick="tab('worker')">Gestão Individual</div>
            </div>
            <button class="btn-pdf" onclick="gerarPDF()">📄 EXPORTAR PDF</button>
        </div>
        <div class="main" id="conteudo-relatorio">
            <div id="market" class="section">
                <h1>Relatório de Mercado</h1>
                <div class="card">{chart_html}</div>
            </div>
            
            <div id="tax" class="section hidden">
                <h1>Simulador Fiscal</h1>
                <div class="card" style="max-width:400px;">
                    <label>Faturamento:</label><input type="number" id="fat" class="input-box">
                    <button onclick="document.getElementById('res-tax').innerHTML='Análise Concluída.'">Simular</button>
                    <div id="res-tax" style="margin-top:10px; color:#ffd700;"></div>
                </div>
            </div>

            <div id="worker" class="section hidden">
                <h1>Gestão CLT vs PJ</h1>
                <div class="card" style="max-width:400px;">
                    <label>Salário:</label><input type="number" id="sal" class="input-box">
                    <button onclick="document.getElementById('res-work').innerHTML='Equivalência PJ calculada.'">Comparar</button>
                    <div id="res-work" style="margin-top:10px; color:#ffd700;"></div>
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

            function gerarPDF() {{
                const elemento = document.getElementById('conteudo-relatorio');
                const opcoes = {{
                    margin: 10,
                    filename: 'Relatorio_MoneyLayer.pdf',
                    image: {{ type: 'jpeg', quality: 0.98 }},
                    html2canvas: {{ scale: 2, backgroundColor: '#050505' }},
                    jsPDF: {{ unit: 'mm', format: 'a4', orientation: 'portrait' }}
                }};
                html2pdf().set(opcoes).from(elemento).save();
            }}
        </script>
    </body>
    </html>
    """
