import os, random, yfinance as yf, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, Form, Request, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional

# --- CONFIGURAÇÃO DE E-MAIL REAL ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "rafael.machado0995@gmail.com"
EMAIL_PASSWORD = "ecqq pkdv mupw kekd" 

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
    token = Column(String)

Base.metadata.create_all(bind=engine)
app = FastAPI()

def send_real_email(destinatario, token):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = destinatario
    msg['Subject'] = f"Código de Acesso MoneyLayer: {token}"
    
    corpo = f"""
    <div style="font-family: sans-serif; background: #000; color: #fff; padding: 30px; border-radius: 10px; border: 1px solid #ffcc00;">
        <h2 style="color: #ffcc00;">MoneyLayer 2.0</h2>
        <p>Seu código de acesso à governança social é:</p>
        <h1 style="background: #111; padding: 20px; text-align: center; border-radius: 5px; color: #ffcc00; letter-spacing: 10px;">{token}</h1>
        <p style="font-size: 12px; color: #555;">The Orbe Systems - Autenticação Soberana</p>
    </div>
    """
    msg.attach(MIMEText(corpo, 'html'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Erro SMTP: {e}")
        return False

@app.get("/", response_class=HTMLResponse)
async def index(cpf_session: Optional[str] = Cookie(None)):
    if not cpf_session:
        return """
        <body style="background:#000; color:#ffcc00; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
            <div style="background:#0a0a0a; padding:40px; border-radius:20px; border:1px solid #222; text-align:center; width:350px;">
                <h1 style="letter-spacing:5px;">MONEYLAYER</h1>
                <form action="/request_access" method="post">
                    <input type="text" name="cpf" placeholder="CPF" style="width:100%; padding:12px; margin:8px 0; border-radius:6px; border:1px solid #333; background:#111; color:#fff;" required>
                    <input type="date" name="birth_date" style="width:100%; padding:12px; margin:8px 0; border-radius:6px; border:1px solid #333; background:#111; color:#fff;" required>
                    <input type="email" name="email" placeholder="E-mail" style="width:100%; padding:12px; margin:8px 0; border-radius:6px; border:1px solid #333; background:#111; color:#fff;" required>
                    <button type="submit" style="width:100%; padding:15px; background:#ffcc00; border:none; border-radius:8px; font-weight:bold; cursor:pointer; margin-top:10px;">SOLICITAR CÓDIGO</button>
                </form>
            </div>
        </body>
        """
    return RedirectResponse(url="/dashboard")

@app.post("/request_access")
async def request_access(cpf: str = Form(...), birth_date: str = Form(...), email: str = Form(...)):
    token = str(random.randint(100000, 999999))
    db = SessionLocal()
    db.add(UserSession(cpf=cpf, email=email, birth_date=birth_date, token=token))
    db.commit()
    db.close()
    
    if send_real_email(email, token):
        return HTMLResponse(f"""
            <body style="background:#000; color:#ffcc00; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh;">
                <div style="text-align:center; border:1px solid #222; padding:40px; border-radius:20px; background:#0a0a0a; width:350px;">
                    <h2>VALIDAR ACESSO</h2>
                    <p style="font-size:12px; color:#666;">Código enviado para: {email}</p>
                    <form action="/verify_token" method="post">
                        <input type="hidden" name="cpf" value="{cpf}">
                        <input type="text" name="token" placeholder="6 DÍGITOS" style="width:100%; padding:15px; border-radius:8px; border:1px solid #333; background:#111; color:#fff; text-align:center;" required>
                        <button type="submit" style="width:100%; padding:15px; background:#ffcc00; border:none; border-radius:8px; font-weight:bold; cursor:pointer; margin-top:20px;">ENTRAR</button>
                    </form>
                </div>
            </body>
        """)
    return "Erro ao enviar e-mail. Verifique se o e-mail está correto."

@app.post("/verify_token")
async def verify_token(cpf: str = Form(...), token: str = Form(...)):
    db = SessionLocal()
    session = db.query(UserSession).filter(UserSession.cpf == cpf, UserSession.token == token).first()
    if session:
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="cpf_session", value=cpf)
        return response
    return "Token inválido."

@app.get("/dashboard")
async def dashboard(cpf_session: Optional[str] = Cookie(None)):
    if not cpf_session: return RedirectResponse(url="/")
    return HTMLResponse(f"<body style='background:#000; color:#ffcc00; padding:40px;'><h1>Soberania Ativa: {cpf_session}</h1><p>Você está conectado à Camada Social.</p><a href='/logout' style='color:#fff;'>Sair</a></body>")

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("cpf_session")
    return response
