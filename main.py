import os, random, yfinance as yf
from fastapi import FastAPI, Form, Request, Cookie, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional

# --- BANCO DE DADOS ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True)
    cpf = Column(String)
    email = Column(String)
    birth_date = Column(String)
    token = Column(String) # Código de acesso enviado por e-mail

class Conversion(Base):
    __tablename__ = "conversions"
    id = Column(Integer, primary_key=True)
    cpf_owner = Column(String)
    brl_value = Column(Float)
    lyr_value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
app = FastAPI()

# Simulação de envio de e-mail
def send_access_token(email, token):
    print(f"\n[SISTEMA ORBE] ENVIANDO TOKEN {token} PARA O E-MAIL: {email}\n")
    # Aqui entraria a lógica real com smtplib

@app.get("/", response_class=HTMLResponse)
async def index(cpf_session: Optional[str] = Cookie(None)):
    if not cpf_session:
        return """
        <html><head><title>MoneyLayer | Cadastro</title>
        <style>
            body { background: #000; color: #ffcc00; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background: #0a0a0a; padding: 30px; border-radius: 15px; border: 1px solid #222; width: 350px; text-align: center; }
            input { background: #111; border: 1px solid #333; color: #fff; padding: 12px; width: 100%; border-radius: 6px; margin: 8px 0; box-sizing: border-box; }
            .btn { background: #ffcc00; color: #000; padding: 15px; width: 100%; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 10px; }
            h1 { letter-spacing: 3px; font-size: 22px; }
        </style></head>
        <body>
            <div class="card">
                <h1>MONEYLAYER 2.0</h1>
                <p style="font-size: 10px; color: #555;">CADASTRO DE INTERESSE SOCIAL</p>
                <form action="/request_access" method="post">
                    <input type="text" name="cpf" placeholder="CPF" required>
                    <input type="date" name="birth_date" title="Data de Nascimento" required>
                    <input type="email" name="email" placeholder="E-mail para receber código" required>
                    <button type="submit" class="btn">SOLICITAR CÓDIGO</button>
                </form>
            </div>
        </body></html>
        """
    return RedirectResponse(url="/dashboard")

@app.post("/request_access")
async def request_access(cpf: str = Form(...), birth_date: str = Form(...), email: str = Form(...)):
    token = str(random.randint(100000, 999999))
    db = SessionLocal()
    # Salva ou atualiza sessão temporária
    session = UserSession(cpf=cpf, email=email, birth_date=birth_date, token=token)
    db.add(session)
    db.commit()
    db.close()
    
    send_access_token(email, token)
    
    return HTMLResponse(f"""
        <body style="background:#000; color:#ffcc00; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh;">
            <div style="text-align:center; border:1px solid #222; padding:30px; border-radius:15px;">
                <h2>CÓDIGO ENVIADO</h2>
                <p>Verifique o e-mail: {email}</p>
                <form action="/verify_token" method="post">
                    <input type="hidden" name="cpf" value="{cpf}">
                    <input type="text" name="token" placeholder="Digite o Código de 6 dígitos" style="padding:12px; border-radius:6px; border:1px solid #333; background:#111; color:#fff; text-align:center;"><br><br>
                    <button type="submit" style="background:#ffcc00; border:none; padding:12px 30px; border-radius:6px; font-weight:bold; cursor:pointer;">ENTRAR NO SISTEMA</button>
                </form>
            </div>
        </body>
    """)

@app.post("/verify_token")
async def verify_token(cpf: str = Form(...), token: str = Form(...)):
    db = SessionLocal()
    session = db.query(UserSession).filter(UserSession.cpf == cpf, UserSession.token == token).first()
    if session:
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="cpf_session", value=cpf)
        return response
    return "Código Inválido. <a href='/'>Tentar novamente</a>"

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(cpf_session: Optional[str] = Cookie(None)):
    if not cpf_session: return RedirectResponse(url="/")
    return f"""<body style='background:#000; color:#eee; font-family:sans-serif; padding:40px;'>
               <h1 style='color:#ffcc00;'>Bem-vindo à Camada Social</h1>
               <p>Identificado via CPF: {cpf_session}</p>
               <hr border-color='#222'>
               <p>Sistema Ativo e Seguro. <a href='/logout' style='color:red;'>Sair</a></p>
               </body>"""

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("cpf_session")
    return response
