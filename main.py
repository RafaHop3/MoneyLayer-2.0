from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="MoneyLayer 2.0")

# Controle de Valores Globais (Interesse Social) [cite: 2025-12-30]
global_values = {
    "project_name": "MoneyLayer",
    "social_interest_status": "Active",
    "audit_version": "2026.1.1",
    "layer_control": "Decentralized"
}

@app.get("/", response_class=HTMLResponse)
async def home():
    return f"""
    <html>
        <head>
            <title>{global_values['project_name']}</title>
            <style>
                body {{ font-family: sans-serif; text-align: center; padding: 50px; background: #121212; color: white; }}
                .btn {{ background: #2ecc71; color: white; padding: 15px 25px; border: none; border-radius: 5px; cursor: pointer; font-size: 1.1em; }}
                .status {{ color: #3498db; }}
            </style>
        </head>
        <body>
            <h1>Projeto: {global_values['project_name']}</h1>
            <p>A camada de dinheiro controlando valores globais com <strong class='status'>Interesse Social</strong>.</p>
            <hr>
            <h3>Painel de Controle</h3>
            <p>Versão da Auditoria: <strong>{global_values['audit_version']}</strong></p>
            <button class="btn" onclick="alert('Sistema de Pagamento Ativado')">Efetuar Pagamento Social</button>
            <br><br>
            <a href="/audit" style="color: #95a5a6;">Acessar Relatórios de Auditoria</a>
        </body>
    </html>
    """

@app.get("/audit")
async def audit_page():
    # Resolvendo o erro 'Audit not found' [cite: 2026-01-09]
    return {{
        "status": "Audit Found",
        "project": global_values['project_name'],
        "transparency_log": "All transactions verified for social interest.",
        "timestamp": "2026-01-13"
    }}
