import os, random, yfinance as yf, plotly.graph_objects as go
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, text
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

def get_market_data():
    try:
        ticker = yf.Ticker("USDBRL=X")
        hist = ticker.history(period="7d")
        return hist
    except:
        return None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    hist = get_market_data()
    val = round(hist['Close'].iloc[-1], 2) if hist is not None else 5.40
    
    return f"""
    <html>
        <head>
            <title>MoneyLayer | Governança Global</title>
            <meta charset="UTF-8">
            <style>
                :root {{ --gold: #ffcc00; --bg: #0a0a0a; --surface: #151515; --text: #eee; }}
                body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 20px; }}
                .container {{ max-width: 480px; margin: auto; }}
                
                .header {{ text-align: center; padding: 20px 0; }}
                h1 {{ color: var(--gold); letter-spacing: 4px; margin: 0; font-size: 24px; }}
                .social-tag {{ font-size: 10px; color: #555; letter-spacing: 2px; }}

                .card {{ background: var(--surface); border: 1px solid #222; border-radius: 16px; padding: 20px; margin-bottom: 20px; }}
                .stat-label {{ font-size: 11px; color: #777; text-transform: uppercase; margin-bottom: 5px; }}
                .stat-value {{ font-size: 32px; font-weight: bold; color: var(--gold); }}

                .converter-box {{ background: #000; border: 1px solid #ffcc0033; border-radius: 12px; padding: 20px; }}
                label {{ font-size: 13px; color: var(--gold); display: block; margin-bottom: 10px; }}
                input {{ background: #1a1a1a; border: 1px solid #333; color: #fff; padding: 12px; width: 100%; border-radius: 8px; box-sizing: border-box; font-size: 16px; }}
                
                .result-area {{ margin-top: 20px; padding-top: 15px; border-top: 1px solid #222; }}
                .res-label {{ font-size: 11px; color: #555; }}
                .res-value {{ font-size: 20px; color: #00ff00; font-weight: bold; }}

                .nav-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 20px; }}
                .nav-item {{ background: var(--surface); border: 1px solid #222; padding: 15px; border-radius: 12px; text-align: center; cursor: pointer; text-decoration: none; color: inherit; }}
                .nav-item:hover {{ border-color: var(--gold); }}

                .footer {{ text-align: center; margin-top: 40px; font-size: 10px; color: #333; line-height: 1.6; }}
            </style>
            <script>
                function calculate() {{
                    const valGlobal = {val};
                    const inputVal = document.getElementById('inputValue').value;
                    const res = (inputVal / valGlobal).toFixed(4);
                    document.getElementById('socialResult').innerText = res + ' LYR';
                }}
            </script>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>MONEYLAYER</h1>
                    <div class="social-tag">SOVEREIGNTY SYSTEM v2.0</div>
                </div>

                <div class="card">
                    <div class="stat-label">Referência Global Atual (USD/BRL)</div>
                    <div class="stat-value">R$ {val}</div>
                </div>

                <div class="converter-box">
                    <label>CONVERSOR DE IMPACTO SOCIAL</label>
                    <input type="number" id="inputValue" placeholder="Valor em BRL (Ex: 100)" oninput="calculate()">
                    
                    <div class="result-area">
                        <div class="res-label">Equivalente em Camada Social:</div>
                        <div id="socialResult" class="res-value">0.0000 LYR</div>
                    </div>
                </div>

                <div class="nav-grid">
                    <a href="/audit" class="nav-item">
                        <div style="font-size: 10px; color: #555;">SISTEMA</div>
                        <div style="font-size: 12px; color: var(--gold);">AUDITORIA</div>
                    </a>
                    <div class="nav-item" onclick="alert('Identificação Requerida')">
                        <div style="font-size: 10px; color: #555;">STATUS</div>
                        <div style="font-size: 12px; color: #00ff00;">ONLINE</div>
                    </div>
                </div>

                <div class="footer">
                    ESTE SISTEMA CALCULA O PODER DE INTERESSE SOCIAL BASEADO EM VALORES GLOBAIS.<br>
                    DESENVOLVIDO POR THE ORBE SYSTEMS
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/audit", response_class=HTMLResponse)
async def audit_page():
    hist = get_market_data()
    if hist is None: return "Erro ao carregar dados."
    fig = go.Figure(data=go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#ffcc00', width=3)))
    fig.update_layout(title="Histórico de Auditoria Global", paper_bgcolor='#0a0a0a', plot_bgcolor='#0a0a0a', font=dict(color='#fff'))
    chart_html = fig.to_html(full_html=False)
    return f"<body style='background:#0a0a0a; color:white; padding:20px;'><a href='/' style='color:#ffcc00; text-decoration:none;'>← Voltar ao Painel</a><br><br>{{chart_html}}</body>"
