import os, random, datetime
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI(title="MoneyLayer 2.0 - Cyber Sentinel")

# Banco de Dados
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos: Usuários e Logs de Intrusão
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    cpf = Column(String, unique=True)
    is_god = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)

class SecurityLog(Base):
    __tablename__ = "security_logs"
    id = Column(Integer, primary_key=True)
    ip_address = Column(String)
    attempted_cpf = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String) # "Sucesso", "Falha", "Banido"

Base.metadata.create_all(bind=engine)

YOUR_GOD_CPF = "86001396000"

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <body style="background:#000; color:#2ecc71; font-family:monospace; text-align:center; padding:50px;">
        <h1 style="color:white;">MONEYLAYER 2.0 - SISTEMA PROTEGIDO</h1>
        <p>[SEGURANÇA DE CAMADA ATIVA]</p>
        <form action="/login" method="post" style="border:1px solid #2ecc71; display:inline-block; padding:20px;">
            <input type="text" name="cpf" placeholder="CPF DE ACESSO" required style="background:#000; color:#2ecc71; border:1px solid #2ecc71; padding:10px;"><br><br>
            <button type="submit" style="background:#2ecc71; color:#000; border:0; padding:10px 20px; font-weight:bold; cursor:pointer;">VALIDAR INTERESSE SOCIAL</button>
        </form>
    </body>
    """

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, cpf: str = Form(...)):
    db = SessionLocal()
    client_ip = request.client.host
    user = db.query(User).filter(User.cpf == cpf).first()
    
    status = "Falha"
    if user:
        if user.is_banned: status = "Banido"
        else: status = "Sucesso"
    
    # Registrar log de segurança [cite: 2026-01-13]
    new_log = SecurityLog(ip_address=client_ip, attempted_cpf=cpf, status=status)
    db.add(new_log)
    
    if status == "Banido":
        db.commit()
        db.close()
        return "<body style='background:red; color:white; text-align:center; padding:100px;'><h1>IP BLOQUEADO: VIOLAÇÃO DETECTADA</h1></body>"

    if not user:
        is_god = (cpf == YOUR_GOD_CPF)
        user = User(cpf=cpf, is_god=is_god)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    if user.is_god:
        all_users = db.query(User).all()
        all_logs = db.query(SecurityLog).order_by(SecurityLog.timestamp.desc()).limit(10).all()
        
        user_list = "".join([f"<li>ID: {u.id} - {u.cpf} {'[BAN]' if u.is_banned else ''}</li>" for u in all_users if not u.is_god])
        log_list = "".join([f"<li>[{l.timestamp.strftime('%H:%M:%S')}] IP: {l.ip_address} - CPF: {l.attempted_cpf} ({l.status})</li>" for l in all_logs])
        
        db.close()
        return f"""
            <body style="background:#000; color:#ffd700; font-family:monospace; padding:30px;">
                <h1 style="text-align:center;">COMANDO SUPREMO - MONEYLAYER</h1>
                <div style="display:flex; justify-content:space-around;">
                    <div style="border:1px solid #ffd700; padding:15px; width:45%;">
                        <h3>AUDITORIA DE USUÁRIOS</h3>
                        <ul>{user_list}</ul>
                    </div>
                    <div style="border:1px solid red; padding:15px; width:45%; color:#ff4444;">
                        <h3>LOGS DE INTRUSÃO (SENTINEL)</h3>
                        <ul>{log_list}</ul>
                    </div>
                </div>
                <p style="text-align:center;"><br><a href="/" style="color:white;">LOGOUT</a></p>
            </body>
        """
    db.commit()
    db.close()
    return f"<body style='background:#000; color:white; text-align:center; padding:50px;'><h1>SISTEMA SOCIAL ATIVO</h1><p>Usuário: {cpf}</p><a href='/'>Voltar</a></body>"
