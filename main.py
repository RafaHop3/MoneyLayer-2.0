import os, random, smtplib, yfinance as yf, plotly.express as px
from email.mime.text import MIMEText
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

app = FastAPI()

# Configurações de Banco e E-mail
DATABASE_URL = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)
EMAIL_USER = "theorbesystems@gmail.com"
EMAIL_PASS = os.getenv("EMAIL_PASSWORD") # Senha de app configurada no Render

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    cpf = Column(String, unique=True)
    email = Column(String)
    last_code = Column(String)
    is_god = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

GOD_CPF = "86001396000"
GOD_EMAIL = "rafael.machado0995@gmail.com"

def send_code(target_email, code):
    msg = MIMEText(f"Seu código de acesso soberano ao MoneyLayer: {code}")
    msg['Subject'] = 'SECURITY TOKEN - THE ORBE SYSTEMS'
    msg['From'] = EMAIL_USER
    msg['To'] = target_email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, target_email, msg.as_string())

@app.get("/", response_class=HTMLResponse)
async def login_step_1():
    return """
    <body style="background:#050505; color:white; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <form action="/auth/identify" method="post" style="background:#111; padding:40px; border-radius:15px; border:1px solid #333; text-align:center;">
            <h1 style="color:#ffd700; letter-spacing:2px;">MONEYLAYER</h1>
            <p style="color:#666;">IDENTIFICAÇÃO DE CAMADA</p>
            <input type="text" name="cpf" placeholder="CPF" required style="padding:15px; width:280px; background:#000; color:#ffd700; border:1px solid #333; border-radius:5px; text-align:center;"><br><br>
            <button type="submit" style="background:#ffd700; color:black; border:0; padding:15px; cursor:pointer; font-weight:bold; width:100%; border-radius:5px;">VERIFICAR</button>
            <div style="margin-top:20px; font-size:0.7em; color:#444;">THE ORBE SYSTEMS</div>
        </form>
    </body>
    """

@app.post("/auth/identify", response_class=HTMLResponse)
async def auth_identify(cpf: str = Form(...)):
    db = SessionLocal()
    clean_cpf = "".join(filter(str.isdigit, cpf))
    code = str(random.randint(100000, 999999))
    
    user = db.query(User).filter(User.cpf == clean_cpf).first()
    
    # Se for o GOD, o e-mail já é fixo e seguro
    if clean_cpf == GOD_CPF:
        email_to_send = GOD_EMAIL
        if not user:
            user = User(cpf=clean_cpf, email=GOD_EMAIL, is_god=True, last_code=code)
            db.add(user)
        else:
            user.last_code = code
    else:
        # Para outros usuários, ainda pediríamos o e-mail ou barraríamos
        db.close()
        return "<h1>Acesso restrito à fase Beta</h1>"

    db.commit()
    send_code(email_to_send, code)
    db.close()

    return f"""
    <body style="background:#050505; color:white; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <form action="/dashboard" method="post" style="background:#111; padding:40px; border-radius:15px; border:1px solid #ffd700; text-align:center;">
            <h2 style="color:#ffd700">TOKEN ENVIADO</h2>
            <p style="color:#888;">Enviado para: {email_to_send[:3]}***@***.com</p>
            <input type="hidden" name="cpf" value="{clean_cpf}">
            <input type="text" name="input_code" placeholder="CÓDIGO DE 6 DÍGITOS" required style="padding:15px; width:280px; background:#000; color:#ffd700; border:1px solid #333; border-radius:5px; text-align:center;"><br><br>
            <button type="submit" style="background:#2ecc71; color:white; border:0; padding:15px; cursor:pointer; font-weight:bold; width:100%; border-radius:5px;">VALIDAR ACESSO</button>
        </form>
    </body>
    """

@app.post("/dashboard", response_class=HTMLResponse)
async def dashboard(cpf: str = Form(...), input_code: str = Form(...)):
    db = SessionLocal()
    user = db.query(User).filter(User.cpf == cpf, User.last_code == input_code).first()
    
    if not user:
        db.close()
        return "<h1>Token Inválido ou Expirado</h1>"

    # Se logou, limpa o código para uso único (Segurança extra)
    user.last_code = None
    db.commit()
    db.close()

    # (AQUI ENTRA O CÓDIGO DO DASHBOARD QUE JÁ FIZEMOS COM THE ORBE SYSTEMS BRANDING)
    return "<h1>Acesso Confirmado. Carregando Camada Soberana...</h1>" # Interface completa aqui
