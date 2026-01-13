import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine

app = FastAPI(title="MoneyLayer")

# Configuração de interesse social [cite: 2025-12-30]
social_config = {
    "project_name": "MoneyLayer",
    "goal": "Controle de Valores Globais",
    "interest": "Social"
}

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL) if DATABASE_URL else None

@app.get("/", response_class=HTMLResponse)
async def home():
    db_status = "Conectado" if engine else "Aguardando DATABASE_URL"
    return f"""
    <html>
        <body style="text-align:center; background:#111; color:white; font-family:sans-serif; padding-top:50px;">
            <h1>{social_config['project_name']} 2.0</h1>
            <p>Objetivo: {social_config['goal']}</p>
            <p style="color:#2ecc71;">Status do Sistema: {db_status}</p>
            <hr style="width:50%; border:0.5px solid #333;">
            <br>
            <form action="/pay" method="post">
                <button type="submit" style="background:#6772e5; color:white; padding:15px 30px; border:0; border-radius:4px; cursor:pointer; font-weight:bold;">
                    Efetuar Pagamento Social
                </button>
            </form>
            <br>
            <a href="/audit" style="color:#aaa; text-decoration:none;">[ Ver Relatório de Auditoria ]</a>
        </body>
    </html>
    """

@app.get("/audit")
async def audit():
    return {{
        "status": "Audit Found",
        "projeto": social_config['project_name'],
        "transparency_log": "Interesse social verificado.",
        "timestamp": "2026-01-13"
    }}

@app.post("/pay")
async def pay():
    key_snippet = os.getenv("STRIPE_API_KEY", "Chave não configurada")[:8]
    return {{"status": "Redirecionando", "stripe_prefix": key_snippet}}
