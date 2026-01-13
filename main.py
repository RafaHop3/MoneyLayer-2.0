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
    
    # Criar gráfico pequeno e elegante para a home
    fig = go.Figure(data=go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#ffcc00', width=2)))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0), height=100,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False), yaxis=dict(visible=False)
    )
    chart_mini = fig.to_html(full_html=False, config={'displayModeBar': False})

    return f"""
    <html>
        <head>
            <title>MoneyLayer | Global Dashboard</title>
            <style>
                :root {{ --gold: #ffcc00; --bg: #0a0a0a; --surface: #151515; }}
                body {{ background: var(--bg); color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; }}
                .container {{ max-width: 500px; margin: auto; }}
                .header {{ text-align: center; margin-bottom: 30px; border-bottom: 1px solid #222; padding-bottom: 20px; }}
                h1 {{ color: var(--gold); letter-spacing: 2px; margin: 0; }}
                .social-tag {{ font-size: 10px; color: #555; }}
                
                .stat-card {{ background: var(--surface); padding: 20px; border-radius: 12px; margin-bottom: 15px; border: 1px solid #222; }}
                .stat-label {{ font-size: 12px; color: #888; text-transform: uppercase; }}
                .stat-value {{ font-size: 28px; font-weight: bold; color: var(--gold); }}
                
                .tool-section {{ background: #000; border: 1px solid #ffcc0033; padding: 20px; border-radius: 12px; }}
                input {{ background: #1a1a1a; border: 1px solid #333; color: var(--gold); padding: 12px; width: 100%; border-radius: 6px; margin: 10px 0; box-sizing: border-box; }}
                .btn {{ background: var(--gold); color: #000; padding: 12px; width: 100%; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }}
                
                .footer {{ text-align: center; margin-top: 40px; font-size: 10px; color: #333; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>MONEYLAYER</h1>
                    <div class="social-tag">THE ORBE SYSTEMS - SOVEREIGNTY UNIT</div>
                </div>

                <div class="stat-card">
                    <div class="stat-label">Valor Global de Referência (USD/BRL)</div>
                    <div class="stat-value">R$ {val}</div>
                    <div style="margin-top:10px;">{chart_mini}</div>
                </div>

                <div class="tool-section">
                    <div style="font-size: 14px; margin-bottom: 10px; font-weight: bold;">VALIDAÇÃO DE IDENTIDADE</div>
                    <form action="/auth/identify" method="post">
                        <input type="text" name="cpf" placeholder="DIGITE SEU CPF" required>
                        <button type="submit" class="btn">ATIVAR CAMADA SOCIAL</button>
                    </form>
                </div>

                <div style="margin-top: 15px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div class="stat-card" style="padding: 15px; margin:0;">
                        <div class="stat-label">Status</div>
                        <div style="color: #00ff00; font-size: 14px;">● ONLINE</div>
                    </div>
                    <div class="stat-card" style="padding: 15px; margin:0; cursor:pointer;" onclick="location.href='/audit'">
                        <div class="stat-label">Auditoria</div>
                        <div style="color: var(--gold); font-size: 14px;">VERIFICAR →</div>
                    </div>
                </div>

                <div class="footer">
                    PROJETO DE INTERESSE SOCIAL PARA CONTROLE DE VALORES GLOBAIS<br>
                    © 2026 THE ORBE SYSTEMS
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
    fig.update_layout(title="Relatório de Auditoria de Câmbio", paper_bgcolor='#0a0a0a', plot_bgcolor='#0a0a0a', font=dict(color='#fff'))
    chart_html = fig.to_html(full_html=False)
    return f"<body style='background:#0a0a0a; color:white; padding:20px;'><a href='/' style='color:#ffcc00;'>← Voltar</a>{chart_html}</body>"

@app.post("/auth/identify")
async def identify(cpf: str = Form(...)):
    return {{"status": "Sucesso", "servico": "MoneyLayer 2.0", "msg": "Valores Globais Sincronizados"}}
