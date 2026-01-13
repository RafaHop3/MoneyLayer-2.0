import os, random, smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

app = FastAPI(title="MoneyLayer 2.0")

# Configurações de Ambiente [cite: 2026-01-13]
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de Usuário com nível GOD
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String, unique=True, index=True)
    email = Column(String, index=True)
    active_code = Column(String)
    is_god = Column(Boolean, default=False) # Poderes exclusivos [cite: 2026-01-13]

Base.metadata.create_all(bind=engine)

# Função para identificar o seu CPF como GOD
YOUR_GOD_CPF = "86001396000" # Seu CPF fornecido anteriormente [cite: 2026-01-13]

@app.post("/auth/request")
async def auth_request(cpf: str = Form(...), email: str = Form(...)):
    db = SessionLocal()
    code = str(random.randint(100000, 999999))
    user = db.query(User).filter(User.cpf == cpf).first()
    
    if not user:
        # Se for o seu CPF, ele nasce como GOD ID 1
        is_god_status = (cpf == YOUR_GOD_CPF)
        user = User(cpf=cpf, email=email, active_code=code, is_god=is_god_status)
        db.add(user)
    else:
        user.active_code = code
    
    db.commit()
    db.close()
    # Lógica de envio de e-mail usando sua senha ecqqpkdvmupwkekd [cite: 2026-01-13]
    return {"status": "success", "is_god_candidate": (cpf == YOUR_GOD_CPF)}

@app.get("/god/panel")
async def god_panel(cpf: str):
    db = SessionLocal()
    user = db.query(User).filter(User.cpf == cpf).first()
    if not user or not user.is_god:
        db.close()
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas para o usuário GOD.")
    
    db.close()
    return {
        "admin": "Bem-vindo, ID 1",
        "powers": "Controle total de valores globais e interesse social",
        "status": "Online 24/7"
    }
