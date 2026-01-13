import os, random, yfinance as yf, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, Form, Request, Cookie, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional

# --- CONFIGURAÇÃO DE E-MAIL ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "rafael.machado0995@gmail.com"
EMAIL_PASSWORD = "ecqq pkdv mupw kekd" 

# --- BANCO DE DADOS ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True)
    cpf = Column(String)
    email = Column(String)
    token = Column(String)

Base.metadata.create_all(bind=engine)
app = FastAPI()

def send_email_task(destinatario, token):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = destinatario
    msg['Subject'] = f"TOKEN: {token} - MoneyLayer"
    
    corpo = f"Seu código de acesso soberano é: {token}"
    msg.attach(MIMEText(corpo, 'plain'))
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"✅ E-mail enviado para {destinatario}")
    except Exception as e:
        print(f"❌ Erro Crítico SMTP: {e}")

@app.get("/", response_class=HTMLResponse)
async def index(cpf_session: Optional[str] = Cookie(None)):
    if not cpf_session:
        return """
        <body style="background:#000; color:#ffcc00; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
            <div style="background:#0a0a0a; padding:40px; border-radius:20px; border:1px solid #222; text-align:center; width:350px;">
                <h1>MONEYLAYER</h1>
                <form action="/request_access" method="post">
                    <input type="text" name="cpf" placeholder="CPF" style="width:100%; padding:12px; margin:8px 0; background:#111; color:#fff; border:1px solid #333;" required>
                    <input type="date" name="birth_date" style="width:100%; padding:12px; margin:8px 0; background:#111; color:#fff; border:1px solid #333;" required>
                    <input type="email" name="email" placeholder="E-mail" style="width:100%; padding:12px; margin:8px 0; background:#111; color:#fff; border:1px solid #333;" required>
                    <button type="submit" style="width:100%; padding:15px; background:#ffcc00; font-weight:bold; cursor:pointer; border:none; border-radius:8px;">SOLICITAR CÓDIGO</button>
                </form>
            </div>
        </body>
        """
    return RedirectResponse(url="/dashboard")

@app.post("/request_access")
async def request_access(background_tasks: BackgroundTasks, cpf: str = Form(...), email: str = Form(...)):
    token = str(random.randint(100000, 999999))
    
    # Salva no banco primeiro
    db = SessionLocal()
    db.add(UserSession(cpf=cpf, email=email, token=token))
    db.commit()
    db.close()
    
    # Dispara o e-mail em background para não travar a tela
    background_tasks.add_task(send_email_task, email, token)
    
    return HTMLResponse(f"""
        <body style="background:#000; color:#ffcc00; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh;">
            <div style="text-align:center; border:1px solid #222; padding:40px; border-radius:20px; background:#0a0a0a; width:350px;">
                <h2>CÓDIGO ENVIADO</h2>
                <p style="color:#666;">Verifique: {email}</p>
                <form action="/verify_token" method="post">
                    <input type="hidden" name="cpf" value="{cpf}">
                    <input type="text" name="token" placeholder="6 DÍGITOS" style="width:100%; padding:15px; background:#111; color:#fff; border:1px solid #333; text-align:center;" required>
                    <button type="submit" style="width:100%; padding:15px; background:#ffcc00; font-weight:bold; cursor:pointer; border:none; border-radius:8px; margin-top:20px;">ENTRAR</button>
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
    return "Token inválido."

@app.get("/dashboard")
async def dashboard(cpf_session: Optional[str] = Cookie(None)):
    if not cpf_session: return RedirectResponse(url="/")
    return HTMLResponse(f"<body style='background:#000; color:#ffcc00; padding:40px;'><h1>Painel Ativo: {cpf_session}</h1></body>")
