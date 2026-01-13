import os
import random
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI(title="MoneyLayer 2.0")

# Configuração do Banco de Dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/dbname")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de Usuário: CPF Único + Email
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String, unique=True, index=True)
    email = Column(String, index=True)
    last_login_code = Column(String)

Base.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
async def login_page():
    return """
    <html>
        <body style="text-align:center; background:#111; color:white; font-family:sans-serif; padding-top:50px;">
            <h1>MoneyLayer 2.0</h1>
            <h3>Acesso ao Painel Social</h3>
            <form action="/login-request" method="post" style="display:inline-block; text-align:left; background:#222; padding:20px; border-radius:8px;">
                <label>CPF (Apenas no primeiro acesso):</label><br>
                <input type="text" name="cpf" placeholder="000.000.000-00" style="width:100%; margin:10px 0; padding:8px;"><br>
                <label>E-mail:</label><br>
                <input type="email" name="email" placeholder="seu@email.com" required style="width:100%; margin:10px 0; padding:8px;"><br>
                <button type="submit" style="width:100%; background:#2ecc71; color:white; border:0; padding:10px; cursor:pointer;">Enviar Código de Acesso</button>
            </form>
            <p style="color:#888; font-size:0.8em;">O código será enviado por theorbesystems@gmail.com</p>
        </body>
    </html>
    """

@app.post("/login-request")
async def login_request(cpf: str = Form(None), email: str = Form(...)):
    db = SessionLocal()
    # Gerar código de 6 dígitos
    otp_code = str(random.randint(100000, 999999))
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        if not cpf:
            return {"error": "CPF necessário para primeiro cadastro"}
        user = User(cpf=cpf, email=email, last_login_code=otp_code)
        db.add(user)
    else:
        user.last_login_code = otp_code
    
    db.commit()
    db.close()
    
    # Aqui entraria a lógica de envio de e-mail real via theorbesystems@gmail.com
    print(f"ENVIANDO EMAIL PARA {email} VIA theorbesystems@gmail.com: Seu código é {otp_code}")
    
    return {
        "status": "Código enviado",
        "message": f"Verifique o e-mail {email}. O código de acesso (senha) foi enviado.",
        "debug_code": otp_code # Remova isso em produção
    }

@app.get("/audit")
async def audit():
    return {"status": "Audit Found", "project": "MoneyLayer", "transparency": "Social Interest Controlled"}
