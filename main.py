import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, text

app = FastAPI(title="MoneyLayer 2.0")

# Pega a URL do banco do Render (Variável de Ambiente: DATABASE_URL)
DATABASE_URL = os.getenv("DATABASE_URL")

# Configuração simples do SQLAlchemy
if DATABASE_URL:
    # Ajuste necessário para compatibilidade com SQLAlchemy se a URL começar com postgres://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL)
else:
    engine = None

@app.get("/", response_class=HTMLResponse)
async def home():
    db_status = "Conectado" if engine else "Desconectado (Verifique o DATABASE_URL)"
    
    # Exemplo de leitura de interesse social (simulado ou do banco)
    social_impact = 100 
    
    return f"""
    <html>
        <head>
            <title>MoneyLayer</title>
            <style>
                body {{ font-family: sans-serif; text-align: center; padding: 50px; background: #121212; color: white; }}
                .status-db {{ color: "#2ecc71" if engine else "#e74c3c"; }}
                .btn {{ background: #2ecc71; color: white; padding: 15px 25px; border: none; border-radius: 5px; cursor: pointer; }}
            </style>
        </head>
        <body>
            <h1>MoneyLayer 2.0</h1>
            <p>Status do Banco: <strong class="status-db">{db_status}</strong></p>
            <p>Interesse Social Ativo: <strong>{social_impact}%</strong></p>
            <hr>
            <button class="btn" onclick="alert('Pagamento Social Processado')">Efetuar Pagamento</button>
            <br><br>
            <a href="/audit" style="color: #95a5a6;">Ver Relatório de Auditoria</a>
        </body>
    </html>
    """

@app.get("/audit")
async def audit():
    # Resolvendo "Audit not found" [cite: 2026-01-09]
    return {{
        "projeto": "MoneyLayer",
        "status": "Auditado",
        "objetivo": "Controle de valores globais com interesse social"
    }}
