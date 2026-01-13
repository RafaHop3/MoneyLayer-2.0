import os, random, smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

app = FastAPI(title="MoneyLayer 2.0")

# Banco de Dados e Conexão [cite: 2025-12-31]
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos: Usuários e Pagamentos Sociais
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    cpf = Column(String, unique=True, index=True)
    email = Column(String, index=True)
    active_code = Column(String)

class SocialPayment(Base):
    __tablename__ = "social_payments"
    id = Column(Integer, primary_key=True)
    user_cpf = Column(String)
    amount = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def send_email(to_email, code):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    msg = MIMEText(f"Seu código MoneyLayer: {code}")
    msg['Subject'] = 'Código de Acesso - MoneyLayer'
    msg['From'] = sender
    msg['To'] = to_email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.sendmail(sender, to_email, msg.as_string())

@app.get("/", response_class=HTMLResponse)
async def login_ui():
    return """
    <body style="text-align:center; background:#000; color:#fff; font-family:sans-serif; padding-top:100px;">
        <h1>MoneyLayer 2.0 CLI Deploy</h1>
        <form action="/auth/request" method="post" style="display:inline-block; background:#111; padding:40px; border:1px solid #333;">
            <input type="text" name="cpf" placeholder="CPF (Novo Cadastro)" style="padding:10px; width:250px;"><br><br>
            <input type="email" name="email" placeholder="E-mail" required style="padding:10px; width:250px;"><br><br>
            <button type="submit" style="background:#2ecc71; color:white; border:0; padding:10px 20px; width:100%;">Enviar Código</button>
        </form>
    </body>
    """

@app.post("/auth/request")
async def auth_request(cpf: str = Form(None), email: str = Form(...)):
    db = SessionLocal()
    code = str(random.randint(100000, 999999))
    user = db.query(User).filter(User.email == email).first()
    if not user:
        if not cpf: return {"error": "CPF obrigatorio"}
        user = User(cpf=cpf, email=email, active_code=code)
        db.add(user)
    else:
        user.active_code = code
    db.commit()
    db.close()
    send_email(email, code)
    return HTMLResponse(f"<h2>Código enviado para {email}!</h2><form action='/auth/verify' method='post'><input type='hidden' name='email' value='{email}'><input type='text' name='code' placeholder='Codigo'><button>Entrar</button></form>")

@app.post("/auth/verify")
async def verify(email: str = Form(...), code: str = Form(...)):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email, User.active_code == code).first()
    if user:
        return {"status": "Acesso Social Liberado", "cpf": user.cpf}
    return {"status": "Erro", "msg": "Codigo invalido"}

@app.get("/audit")
async def audit():
    return {"status": "Audit Found", "project": "MoneyLayer", "transparency": "Social Interest [cite: 2026-01-09]"}
