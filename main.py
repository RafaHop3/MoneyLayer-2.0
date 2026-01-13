import os, random, time
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI(title="MoneyLayer 2.0 Security Plus")

# Banco de Dados
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo com campos de segurança
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    cpf = Column(String, unique=True)
    is_god = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False) # Função de bloqueio

Base.metadata.create_all(bind=engine)

YOUR_GOD_CPF = "86001396000"

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY" # Previne Clickjacking
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <body style="background:#000; color:#2ecc71; font-family:monospace; text-align:center; padding:50px;">
        <h1 style="color:white;">MONEYLAYER 2.0 - PROTEÇÃO ATIVA</h1>
        <p>[SISTEMA MONITORADO CONTRA INTRUSÃO]</p>
        <form action="/login" method="post" style="border:1px solid #2ecc71; display:inline-block; padding:20px;">
            <input type="text" name="cpf" placeholder="IDENTIFICAÇÃO" required style="background:#000; color:#2ecc71; border:1px solid #2ecc71; padding:10px;"><br><br>
            <button type="submit" style="background:#2ecc71; color:#000; border:0; padding:10px 20px; font-weight:bold; cursor:pointer;">ACESSAR CAMADA</button>
        </form>
    </body>
    """

@app.post("/login", response_class=HTMLResponse)
async def login(cpf: str = Form(...)):
    db = SessionLocal()
    # Proteção básica contra SQL Injection via ORM
    user = db.query(User).filter(User.cpf == cpf).first()
    
    if user and user.is_banned:
        db.close()
        return "<body style='background:red; color:white; text-align:center; padding:100px;'><h1>ACESSO BLOQUEADO POR VIOLAÇÃO DE INTERESSE SOCIAL</h1></body>"

    if not user:
        is_god = (cpf == YOUR_GOD_CPF)
        user = User(cpf=cpf, is_god=is_god)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    if user.is_god:
        all_users = db.query(User).all()
        user_list = "".join([
            f"<li>ID: {u.id} - CPF: {u.cpf} {'[BANNED]' if u.is_banned else ''} " 
            f"<form action='/ban' method='post' style='display:inline;'><input type='hidden' name='target' value='{u.cpf}'><button type='submit'>Bloquear</button></form></li>" 
            for u in all_users if not u.is_god
        ])
        db.close()
        return f"""
            <body style="background:#000; color:#ffd700; font-family:monospace; text-align:center; padding:50px;">
                <h1>PAINEL GOD - MODO DEFESA</h1>
                <div style="border:2px solid #ffd700; padding:20px; text-align:left; display:inline-block;">
                    <h3>CONTROLE DE ACESSOS E AUDITORIA</h3>
                    <ul>{user_list}</ul>
                </div>
                <br><br><a href="/" style="color:white;">Sair</a>
            </body>
        """
    db.close()
    return f"<body style='background:#000; color:white; text-align:center; padding:50px;'><h1>LOGIN REALIZADO</h1><p>CPF: {cpf}</p><a href='/'>Voltar</a></body>"

@app.post("/ban")
async def ban_user(target: str = Form(...)):
    db = SessionLocal()
    user = db.query(User).filter(User.cpf == target).first()
    if user and not user.is_god:
        user.is_banned = True
        db.commit()
    db.close()
    return HTMLResponse("<script>alert('Usuário banido!'); window.location.href='/';</script>")
