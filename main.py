from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from models import MoneyLayerStatus, GlobalControls

app = FastAPI()

# ---------------------------------------------------------
# 1. DEFINIÇÃO DAS REGRAS (GOVERNANÇA)
# ---------------------------------------------------------
# Aqui definimos os valores reais.
# O sistema vai validar se o CEO ganha no máximo 10x o menor salário.
social_rules = GlobalControls(
    max_transaction_fee=2.5,          # Taxa de 2.5% (O limite técnico é 5%)
    social_redistribution_rate=15.0,  # 15% do lucro volta para a comunidade
    min_employee_salary=2000.00,      # Menor salário da empresa
    ceo_salary=15000.00               # Seu salário (7.5x a base, dentro do limite de 10x)
)

# ---------------------------------------------------------
# 2. INICIALIZAÇÃO DO ESTADO
# ---------------------------------------------------------
current_state = MoneyLayerStatus(
    status="active",
    service="Money Layer",
    social_mission="Financial access for all",
    version="MVP 1.1",
    governance=social_rules
)

# ---------------------------------------------------------
# 3. ENDPOINTS DA API
# ---------------------------------------------------------

# Rota de Dados (O Frontend consome isso)
@app.get("/status")
def get_status():
    return current_state

# ---------------------------------------------------------
# 4. SERVIDOR DE ARQUIVOS ESTATICOS (FRONTEND)
# ---------------------------------------------------------

# Monta a pasta 'static' para servir CSS/JS/Imagens se precisar
app.mount("/static", StaticFiles(directory="static"), name="static")

# Rota Raiz: Entrega o index.html quando acessa o site
@app.get("/")
async def read_index():
    return FileResponse('static/index.html')