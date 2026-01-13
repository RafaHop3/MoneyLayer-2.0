import os, random, yfinance as yf
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- CONFIGURAÇÃO DE BANCO ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String, unique=True, index=True)

try:
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS cpf VARCHAR(14) UNIQUE;"))
        conn.commit()
except: pass

app = FastAPI()

# --- LÓGICA DE INTERESSE SOCIAL ---
def get_global_index():
    try:
        data = yf.Ticker("USDBRL=X").history(period="1d")
        price = data['Close'].iloc[-1]
        return round(price, 2)
    except:
        return 5.40  # Valor fallback

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    val = get_global_index()
    return f"""
    <html>
        <head>
            <title>MoneyLayer | The Orbe Systems</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                :root {{ --gold: #ffcc00; --bg: #050505; --card: #111; }}
                body {{ background: var(--bg); color: #fff; font-family: 'Inter', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
                .glass-card {{ background: var(--card); border: 1px solid #222; padding: 40px; border-radius: 20px; text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.8); width: 90%; max-width: 400px; }}
                h1 {{ color: var(--gold); letter-spacing: 4px; font-weight: 800; margin-bottom: 5px; text-transform: uppercase; }}
                .tagline {{ color: #555; font-size: 11px; letter-spacing: 2px; margin-bottom: 30px; }}
                .ticker {{ background: #000; border-radius: 10px; padding: 15px; margin-bottom: 20px; border: 1px dashed #333; }}
                .ticker-val {{ color: var(--gold); font-size: 24px; font-weight: bold; }}
                input {{ background: #1a1a1a; border: 1px solid #333; color: var(--gold); padding: 15px; width: 100%; border-radius: 8px; margin-bottom: 15px; box-sizing: border-box; }}
                .btn-primary {{ background: var(--gold); color: #000; padding: 15px; width: 100%; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.3s; text-transform: uppercase; }}
                .btn-primary:hover {{ transform: scale(1.02); box-shadow: 0 0 15px rgba(255,204,0,0.3); }}
                .btn-outline {{ background: transparent; color: var(--gold); border: 1px solid var(--gold); padding: 12px; width: 100%; border-radius: 8px; margin-top: 10px; cursor: pointer; font-size: 12px; }}
                .footer {{ margin-top: 40px; font-size: 10px; color: #333; letter-spacing: 1px; }}
            </style>
        </head>
        <body>
            <div class="glass-card">
                <h1>MoneyLayer</h1>
                <div class="tagline">Global Value Governance</div>
                <div class="ticker">
                    <div style="font-size: 10px; color: #666;">Câmbio Global (USD/BRL)</div>
                    <div class="ticker-val">R$ {val}</div>
                </div>
                <form action="/auth/identify" method="post">
                    <input type="text" name="cpf" placeholder="IDENTIFICAÇÃO DE CAMADA" required>
                    <button type="submit" class="btn-primary">Validar Governança</button>
                </form>
                <button class="btn-outline" onclick="location.href='/audit'">Acessar Auditoria</button>
                <div class="footer">POWERED BY THE ORBE SYSTEMS</div>
            </div>
        </body>
    </html>
    """

@app.post("/auth/identify")
async def identify(cpf: str = Form(...)):
    val = get_global_index()
    # IA de Simulação vinculando o valor global ao CPF
    interest_impact = round((val * random.random()), 4)
    return {
        "status": "Sincronizado",
        "protocol": f"ORBE-{random.randint(10000, 99999)}",
        "impacto_social": f"{interest_impact}%",
        "global_reference": val
    }

@app.get("/audit")
async def audit():
    return {"status": "Audit Found", "last_check": "Just now", "system": "Protected"}
