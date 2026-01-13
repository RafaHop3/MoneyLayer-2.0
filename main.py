import os, random, yfinance as yf
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Banco de Dados
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
    # Aqui simulamos a validação do código para focar na UX do Dashboard
    return f"""
    <html>
    <head>
        <style>
            body {{ margin: 0; font-family: 'Segoe UI', sans-serif; background: #050505; color: white; display: flex; height: 100vh; }}
            .sidebar {{ width: 220px; background: #111; border-right: 1px solid #222; padding: 20px; display: flex; flex-direction: column; gap: 10px; }}
            .content {{ flex: 1; padding: 40px; overflow-y: auto; }}
            .nav-tabs {{ display: flex; gap: 20px; border-bottom: 1px solid #333; margin-bottom: 20px; }}
            .tab-link {{ padding: 10px 20px; cursor: pointer; color: #888; border-bottom: 2px solid transparent; }}
            .tab-link.active {{ color: #ffd700; border-bottom-color: #ffd700; font-weight: bold; }}
            .sub-section {{ display: none; }}
            .sub-section.active {{ display: block; }}
            .card {{ background: #161616; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #222; }}
            .btn-sub {{ background: #222; color: #ccc; border: none; padding: 10px; text-align: left; cursor: pointer; border-radius: 5px; }}
            .btn-sub:hover {{ background: #333; color: #fff; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2 style="color:#ffd700; font-size: 1.2em;">MoneyLayer 2.0</h2>
            <p style="font-size: 0.8em; color: #666;">ID SOBERANO: 001</p>
            <hr style="width: 100%; border-color: #222;">
            <p style="font-size: 0.7em; color: #ffd700;">SUB-MENU</p>
            <button class="btn-sub" onclick="showSub('caixa')">Fluxo de Caixa</button>
            <button class="btn-sub" onclick="showSub('tributos')">Tributação</button>
            <button class="btn-sub" onclick="showSub('reserva')">Reserva de Emergência</button>
        </div>
        <div class="content">
            <div class="nav-tabs">
                <div id="tab-empresa" class="tab-link active" onclick="switchMain('empresa')">GERENCIAMENTO EMPRESA</div>
                <div id="tab-trabalhador" class="tab-link" onclick="switchMain('trabalhador')">GERENCIAMENTO TRABALHADOR</div>
            </div>

            <div id="sec-empresa" class="main-section active">
                <div id="caixa" class="sub-section active">
                    <div class="card">
                        <h3>Visão: Fluxo de Caixa (Empresa)</h3>
                        <p style="color: #2ecc71;">Sugestão MoneyLayer: Mantenha 3 meses de custos fixos em liquidez diária.</p>
                        <canvas id="chartCaixa"></canvas>
                    </div>
                </div>
                <div id="tributos" class="sub-section">
                    <div class="card"><h3>Visão: Planejamento Tributário</h3><p>Análise de Simples Nacional vs Lucro Presumido.</p></div>
                </div>
            </div>

            <div id="sec-trabalhador" class="main-section" style="display:none;">
                <div id="reserva" class="sub-section active">
                    <div class="card">
                        <h3>Visão: Reserva de Emergência (Pessoa Física)</h3>
                        <p>Otimização: Alocar 15% do salário em Tesouro Selic até atingir 6 meses de gastos.</p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            function switchMain(target) {{
                document.querySelectorAll('.main-section').forEach(el => el.style.display = 'none');
                document.querySelectorAll('.tab-link').forEach(el => el.classList.remove('active'));
                
                if(target === 'empresa') {{
                    document.getElementById('sec-empresa').style.display = 'block';
                    document.getElementById('tab-empresa').classList.add('active');
                }} else {{
                    document.getElementById('sec-trabalhador').style.display = 'block';
                    document.getElementById('tab-trabalhador').classList.add('active');
                }}
            }}

            function showSub(id) {{
                document.querySelectorAll('.sub-section').forEach(el => el.classList.remove('active'));
                document.getElementById(id).classList.add('active');
            }}
        </script>
    </body>
    </html>
    """
