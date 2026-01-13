import os, random
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuração de Banco de Dados Resiliente (Render + Local)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)

# Migração Automática de Coluna
try:
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS cpf VARCHAR(14) UNIQUE;"))
        conn.commit()
except Exception as e:
    print(f"Migration Status: {e}")

app = FastAPI(title="MoneyLayer 2.0")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return """
    <html>
        <head>
            <title>MoneyLayer 2.0 | Orbe Systems</title>
            <style>
                body { background: #000; color: #fff; font-family: 'Courier New', monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                .panel { border: 1px solid #ffcc00; padding: 40px; border-radius: 5px; text-align: center; background: #050505; box-shadow: 0 0 20px rgba(255, 204, 0, 0.2); width: 400px; }
                h1 { color: #ffcc00; font-size: 28px; letter-spacing: 5px; margin-bottom: 5px; }
                .social-tag { color: #444; font-size: 10px; margin-bottom: 30px; letter-spacing: 2px; }
                input { background: #000; border: 1px solid #333; color: #ffcc00; padding: 15px; width: 100%; box-sizing: border-box; margin-bottom: 10px; text-align: center; }
                .btn { background: #ffcc00; color: #000; padding: 15px; width: 100%; border: none; font-weight: bold; cursor: pointer; text-transform: uppercase; margin-bottom: 10px; }
                .btn-audit { background: transparent; color: #555; border: 1px solid #222; font-size: 11px; padding: 8px; width: 100%; cursor: pointer; }
                .brand { margin-top: 40px; color: #333; font-size: 10px; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="panel">
                <h1>MONEYLAYER</h1>
                <div class="social-tag">GLOBAL GOVERNANCE & SOCIAL INTEREST</div>
                <form action="/auth/identify" method="post">
                    <input type="text" name="cpf" placeholder="IDENTIFICAÇÃO (CPF)" required>
                    <button type="submit" class="btn">Validar Camada</button>
                </form>
                <button class="btn" style="background: #111; color: #ffcc00; border: 1px solid #ffcc00;" onclick="alert('Iniciando Pagamento de Auditoria Social...')">Efetuar Pagamento</button>
                <button class="btn-audit">RELATÓRIO DE AUDITORIA DISPONÍVEL</button>
                <div class="brand">THE ORBE SYSTEMS</div>
            </div>
        </body>
    </html>
    """

@app.post("/auth/identify")
async def identify(cpf: str = Form(...)):
    # Simulação IA de Interesse Social
    val_global = round(random.uniform(1.1, 9.9), 2)
    return {
        "status": "Acesso Autorizado",
        "governance_token": f"SOC-{random.randint(1000, 9999)}",
        "social_interest_index": f"{val_global}%",
        "message": "Valores globais sincronizados com o CPF informado."
    }

@app.get("/health")
async def health():
    return {"status": "online", "version": "2.0.1"}
