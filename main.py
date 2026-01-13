import os, random
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuração de Banco de Dados Resiliente
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL or "sqlite:///./test.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String(14), unique=True, index=True)

# Tenta criar a tabela/coluna automaticamente no startup
try:
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS cpf VARCHAR(14) UNIQUE;"))
        conn.commit()
except Exception as e:
    print(f"Aviso na migração: {e}")

app = FastAPI(title="MoneyLayer 2.0")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return """
    <html>
        <head>
            <title>MoneyLayer 2.0 - Sovereignty</title>
            <style>
                body { background: #0a0a0a; color: #eee; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                .container { background: #111; padding: 40px; border-radius: 15px; border: 1px solid #333; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; width: 350px; }
                h1 { color: #ffcc00; letter-spacing: 2px; margin-bottom: 5px; }
                .subtitle { color: #666; font-size: 12px; margin-bottom: 30px; text-transform: uppercase; }
                input { width: 100%; padding: 12px; margin: 10px 0; background: #000; border: 1px solid #444; color: #ffcc00; border-radius: 5px; text-align: center; }
                .btn-verify { width: 100%; padding: 12px; background: #ffcc00; color: #000; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; transition: 0.3s; }
                .btn-verify:hover { background: #e6b800; }
                .btn-pay { margin-top: 15px; background: transparent; color: #ffcc00; border: 1px solid #ffcc00; width: 100%; padding: 10px; border-radius: 5px; cursor: pointer; }
                .footer { margin-top: 30px; font-size: 10px; color: #444; letter-spacing: 1px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>MONEYLAYER</h1>
                <div class="subtitle">Identificação de Camada</div>
                <form action="/auth/identify" method="post">
                    <input type="text" name="cpf" placeholder="000.000.000-00" required>
                    <button type="submit" class="btn-verify">VERIFICAR</button>
                </form>
                <button class="btn-pay" onclick="alert('Sistema de Auditoria: Redirecionando para Gateway de Pagamento Social...')">EFETUAR PAGAMENTO</button>
                <div class="footer">THE ORBE SYSTEMS</div>
            </div>
        </body>
    </html>
    """

@app.post("/auth/identify")
async def identify(cpf: str = Form(...)):
    # Aqui entra sua lógica de interesse social e controle global
    return {"status": "Processando", "camada": "Social Interest v1", "cpf_detectado": cpf}

@app.get("/health")
async def health():
    return {"status": "active", "service": "MoneyLayer 2.0"}
