import os, random, smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Configurações de Banco e E-mail
DATABASE_URL = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)
EMAIL_USER = "theorbesystems@gmail.com"
EMAIL_PASS = os.getenv("EMAIL_PASSWORD") # A senha de app 'ecqqpkdvmupwkekd' deve estar no Render

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

def send_security_email(target_email, code):
    msg = MIMEText(f"Seu código de acesso MoneyLayer: {code}")
    msg['Subject'] = 'Código de Acesso - Segurança Camada 2.0'
    msg['From'] = EMAIL_USER
    msg['To'] = target_email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, target_email, msg.as_string())

@app.get("/", response_class=HTMLResponse)
async def login_step_1():
    return """
    <body style="background:#000; color:#fff; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <form action="/auth/step2" method="post" style="text-align:center; border:1px solid #333; padding:40px; border-radius:15px;">
            <h2 style="color:#ffd700">MONEYLAYER</h2>
            <p style="color:#888;">Digite seu CPF para iniciar</p>
            <input type="text" name="cpf" placeholder="000.000.000-00" required style="padding:12px; border-radius:5px; border:1px solid #444; background:#111; color:#fff; width:250px;"><br><br>
            <button type="submit" style="background:#ffd700; border:0; padding:12px 25px; font-weight:bold; cursor:pointer; width:100%;">CONTINUAR</button>
        </form>
    </body>
    """

@app.post("/auth/step2", response_class=HTMLResponse)
async def login_step_2(cpf: str = Form(...)):
    clean_cpf = "".join(filter(str.isdigit, cpf))
    return f"""
    <body style="background:#000; color:#fff; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <form action="/auth/verify" method="post" style="text-align:center; border:1px solid #333; padding:40px; border-radius:15px;">
            <h2 style="color:#ffd700">VALIDAÇÃO</h2>
            <input type="hidden" name="cpf" value="{clean_cpf}">
            <p style="color:#888;">Informe seu e-mail para receber o código</p>
            <input type="email" name="email" placeholder="seu@email.com" required style="padding:12px; border-radius:5px; border:1px solid #444; background:#111; color:#fff; width:250px;"><br><br>
            <button type="submit" style="background:#ffd700; border:0; padding:12px 25px; font-weight:bold; cursor:pointer; width:100%;">ENVIAR CÓDIGO</button>
        </form>
    </body>
    """

@app.post("/auth/verify", response_class=HTMLResponse)
async def verify_code(cpf: str = Form(...), email: str = Form(...)):
    db = SessionLocal()
    code = str(random.randint(100000, 999999))
    
    user = db.query(User).filter(User.cpf == cpf).first()
    if not user:
        # Se for o seu CPF, cria como GOD ID 1
        is_god = (cpf == "86001396000")
        user = User(cpf=cpf, email=email, last_code=code, is_god=is_god)
        db.add(user)
    else:
        user.last_code = code
        user.email = email
    
    db.commit()
    send_security_email(email, code)
    db.close()

    return f"""
    <body style="background:#000; color:#fff; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <form action="/dashboard" method="post" style="text-align:center; border:1px solid #333; padding:40px; border-radius:15px;">
            <h2 style="color:#ffd700">CÓDIGO ENVIADO</h2>
            <p style="color:#888;">Verifique theorbesystems@gmail.com</p>
            <input type="hidden" name="cpf" value="{cpf}">
            <input type="text" name="input_code" placeholder="Digite o código" required style="padding:12px; border-radius:5px; border:1px solid #444; background:#111; color:#fff; width:250px;"><br><br>
            <button type="submit" style="background:#2ecc71; border:0; padding:12px 25px; font-weight:bold; cursor:pointer; width:100%;">ACESSAR DASHBOARD</button>
        </form>
    </body>
    """

@app.post("/dashboard", response_class=HTMLResponse)
async def final_dashboard(cpf: str = Form(...), input_code: str = Form(...)):
    db = SessionLocal()
    user = db.query(User).filter(User.cpf == cpf, User.last_code == input_code).first()
    db.close()
    
    if not user:
        return "<h1>Código inválido ou expirado</h1>"
    
    return f"<h1>Bem-vindo ao Dashboard SOBERANO ID: {user.id}</h1><p>Usuário reconhecido.</p>"

