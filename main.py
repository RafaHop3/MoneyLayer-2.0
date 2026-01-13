import os, random, smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI(title="MoneyLayer 2.0")

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL) if DATABASE_URL else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    cpf = Column(String, unique=True)
    email = Column(String)
    active_code = Column(String)

if engine:
    Base.metadata.create_all(bind=engine)

@app.get("/")
def home(): return {"status": "MoneyLayer Online", "interest": "Social"}

@app.post("/auth/request")
async def auth_request(cpf: str = Form(None), email: str = Form(...)):
    db = SessionLocal()
    try:
        code = str(random.randint(100000, 999999))
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(cpf=cpf, email=email, active_code=code)
            db.add(user)
        else:
            user.active_code = code
        db.commit()
        # Lógica de e-mail aqui (usando EMAIL_USER e EMAIL_PASSWORD do Render)
        return {"status": "success", "message": "Codigo enviado para " + email}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    finally:
        db.close()

@app.get("/audit")
def audit(): return {"status": "Audit Found", "project": "MoneyLayer"}
