import os, yfinance as yf, plotly.express as px
from fastapi import FastAPI, Form, Request, HTTPException, Header
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

app = FastAPI()

# Database & Security
DATABASE_URL = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class GlobalValue(Base):
    __tablename__ = "global_values"
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)
    value = Column(Float)

Base.metadata.create_all(bind=engine)

GOD_CPF = "86001396000"
MASTER_API_KEY = os.getenv("MONEYLAYER_API_KEY", "padrao_seguro_123")

@app.post("/dashboard", response_class=HTMLResponse)
async def dashboard(cpf: str = Form(...), input_code: str = Form(...)):
    db = SessionLocal()
    clean_cpf = "".join(filter(str.isdigit, cpf))
    is_admin = (clean_cpf == GOD_CPF)
    
    social_index = db.query(GlobalValue).filter(GlobalValue.key == "social_multiplier").first()
    idx_val = social_index.value if social_index else 1.0
    db.close()

    assets = ["USDBRL=X", "BTC-USD"]
    data = yf.download(assets, period="5d", interval="1h")['Close']
    chart_html = px.line(data, template="plotly_dark").to_html(full_html=False)

    return f"""
    <html>
    <head>
        <style>
            body {{ margin: 0; background: #050505; color: #fff; font-family: 'Inter', sans-serif; display: flex; height: 100vh; }}
            .sidebar {{ 
                width: 280px; background: #000; border-right: 1px solid #222; padding: 25px; 
                display: flex; flex-direction: column; justify-content: space-between;
            }}
            .main {{ flex: 1; padding: 40px; overflow-y: auto; background: radial-gradient(circle at 0% 0%, #111 0%, #050505 100%); }}
            .nav-item {{ padding: 12px; cursor: pointer; color: #888; border-radius: 8px; margin-bottom: 5px; transition: 0.3s; }}
            .active {{ background: #1a1a1a; color: #ffd700; border-left: 3px solid #ffd700; }}
            
            /* Assinatura The Orbe Systems */
            .author-brand {{ 
                text-align: center; padding: 20px; border-top: 1px solid #222; 
                filter: drop-shadow(0 0 5px rgba(255, 215, 0, 0.2));
            }}
            .orbe-logo {{ 
                font-size: 0.7em; letter-spacing: 4px; color: #555; text-transform: uppercase; margin-bottom: 5px; 
            }}
            .orbe-name {{ 
                font-size: 0.9em; font-weight: bold; color: #ffd700; text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
            }}
            .card {{ background: #111; border: 1px solid #222; padding: 20px; border-radius: 12px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div>
                <h2 style="color:#ffd700; letter-spacing:2px;">MONEYLAYER</h2>
                <div class="nav-item active">Painel Global</div>
                {"<div class='nav-item'>🔐 Governação</div>" if is_admin else ""}
            </div>
            
            <div class="author-brand">
                <div class="orbe-logo">Engineered by</div>
                <div class="orbe-name">THE ORBE SYSTEMS</div>
            </div>
        </div>
        <div class="main">
            <h1>Inteligência Estratégica</h1>
            <div class="card">{chart_html}</div>
        </div>
    </body>
    </html>
    """
