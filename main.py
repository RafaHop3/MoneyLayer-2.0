import os, yfinance as yf, plotly.express as px
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

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

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    cpf_attempt = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

GOD_CPF = "86001396000"

@app.post("/dashboard", response_class=HTMLResponse)
async def dashboard(cpf: str = Form(...), input_code: str = Form(...)):
    db = SessionLocal()
    clean_cpf = "".join(filter(str.isdigit, cpf))
    
    # Registro de Auditoria
    new_log = AuditLog(cpf_attempt=clean_cpf)
    db.add(new_log)
    db.commit()

    # Verificação de Poder SOBERANO
    is_admin = (clean_cpf == GOD_CPF)
    
    # Busca de dados de mercado
    assets = ["USDBRL=X", "BTC-USD"]
    data = yf.download(assets, period="5d", interval="1h")['Close']
    chart_html = px.line(data, template="plotly_dark").to_html(full_html=False)

    # Lista de auditoria (Apenas para GOD)
    audit_list = ""
    if is_admin:
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10).all()
        audit_list = "".join([f"<li>[{l.timestamp.strftime('%H:%M')}] CPF: {l.cpf_attempt}</li>" for l in logs])

    db.close()

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
            .admin-only {{ border: 1px solid #ffd700; color: #ffd700; padding: 15px; border-radius: 10px; margin-top: 20px; }}
            .btn-pdf {{ background: #e74c3c; color: white; border:0; padding:12px; border-radius:5px; cursor:pointer; width:100%; font-weight:bold; }}
            .hidden {{ display: none; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2 style="color:#ffd700">MONEYLAYER <span style="font-weight:200">2.0</span></h2>
            <div class="nav-item active" onclick="tab('market')">Mercado Global</div>
            <div class="nav-item" onclick="tab('tax')">Gestão Business</div>
            {"<div class='nav-item' onclick='tab(\"admin\")'>🔐 AUDITORIA</div>" if is_admin else ""}
            <button class="btn-pdf" onclick="gerarPDF()">📄 EXPORTAR RELATÓRIO</button>
        </div>
        <div class="main" id="relatorio">
            <div id="market" class="section">
                <h1>Monitor de Inteligência</h1>
                <div class="card">{chart_html}</div>
            </div>
            
            <div id="admin" class="section hidden">
                <h1>Painel de Controle Soberano</h1>
                <div class="admin-only">
                    <h3>Últimos Acessos ao Sistema (Interesse Social)</h3>
                    <ul>{audit_list}</ul>
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
                const element = document.getElementById('relatorio');
                html2pdf().set({{ margin: 10, filename: 'MoneyLayer_Audit.pdf', html2canvas: {{ scale: 2, backgroundColor: '#050505' }} }}).from(element).save();
            }}
        </script>
    </body>
    </html>
    """
