import os, random
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI(title="MoneyLayer 2.0")

# Banco de Dados
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    cpf = Column(String, unique=True)
    is_god = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

YOUR_GOD_CPF = "86001396000"

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <body style="background:#000; color:#2ecc71; font-family:monospace; text-align:center; padding:50px;">
        <h1 style="color:white;">MONEYLAYER 2.0 - SISTEMA ATIVO</h1>
        <p>Aguardando Identificação de Interesse Social...</p>
        <form action="/login" method="post" style="border:1px solid #2ecc71; display:inline-block; padding:20px;">
            <input type="text" name="cpf" placeholder="DIGITE SEU CPF" style="background:#000; color:#2ecc71; border:1px solid #2ecc71; padding:10px;"><br><br>
            <button type="submit" style="background:#2ecc71; color:#000; border:0; padding:10px 20px; font-weight:bold; cursor:pointer;">ACESSAR CAMADA</button>
        </form>
    </body>
    """

@app.post("/login")
async def login(cpf: str = Form(...)):
    db = SessionLocal()
    user = db.query(User).filter(User.cpf == cpf).first()
    
    if not user:
        is_god = (cpf == YOUR_GOD_CPF)
        user = User(cpf=cpf, is_god=is_god)
        db.add(user)
        db.commit()
    
    if user.is_god:
        return HTMLResponse(f"""
            <body style="background:#000; color:#ffd700; font-family:monospace; text-align:center; padding:50px;">
                <h1>BEM-VINDO, USUÁRIO GOD (ID 1)</h1>
                <p>STATUS: CONTROLE TOTAL ATIVADO</p>
                <div style="border:2px solid #ffd700; padding:20px; margin-top:20px;">
                    <h3>CONTROLE DE VALORES GLOBAIS</h3>
                    <button style="padding:10px;">AJUSTAR TAXA SOCIAL</button>
                    <button style="padding:10px;">AUDITAR PAGAMENTOS</button>
                </div>
            </body>
        """)
    return {"status": "Acesso Comum", "cpf": cpf}
