from dotenv import load_dotenv
import os, stripe, psycopg2, random
from flask import Flask, render_template_string, request, redirect, session

load_dotenv()
app = Flask(__name__)
app.secret_key = 'chave-nuclear-money-layer'

# --- CONFIGURAÇÕES ---
stripe.api_key = os.getenv("STRIPE_API_KEY")

def get_db():
    return psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')

# --- HTML DA HOME (LOGIN + STRIPE) ---
HOME_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>MoneyLayer Global</title>
    <style>
        body { font-family: 'Arial', sans-serif; background: #e9ecef; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .main-card { display: flex; width: 800px; background: white; box-shadow: 0 10px 30px rgba(0,0,0,0.2); border-radius: 12px; overflow: hidden; }
        .left { flex: 1; padding: 40px; background: #fff; border-right: 1px solid #ddd; }
        .right { flex: 1; padding: 40px; background: #f8f9fa; text-align: center; }
        h2 { margin-top: 0; color: #333; }
        input { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        .btn { width: 100%; padding: 10px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-top: 10px; }
        .btn-green { background: #28a745; color: white; }
        .btn-black { background: #343a40; color: white; }
        .btn-stripe { background: #6772e5; color: white; padding: 15px; font-size: 16px; display: flex; align-items: center; justify-content: center; gap: 10px; }
        .divider { border-top: 1px solid #eee; margin: 25px 0; position: relative; }
        .divider:after { content: 'OU'; position: absolute; top: -10px; left: 45%; background: white; padding: 0 5px; color: #888; font-size: 12px; }
    </style>
</head>
<body>
    <div class="main-card">
        <div class="left">
            <h2>🔐 Acesso Seguro</h2>
            
            <form action="/gerar_token" method="POST">
                <label style="font-size:12px; font-weight:bold; color:#555;">PASSO 1: OBTER CÓDIGO</label>
                <input type="email" name="email" placeholder="E-mail" required>
                <input type="text" name="cpf" placeholder="CPF" required>
                <button type="submit" class="btn btn-green">GERAR CÓDIGO</button>
            </form>

            <div class="divider"></div>

            <form action="/login" method="POST">
                <label style="font-size:12px; font-weight:bold; color:#555;">PASSO 2: ENTRAR</label>
                <input type="email" name="email" placeholder="Confirme E-mail" required>
                <input type="text" name="token" placeholder="Código de 6 Dígitos" required>
                <button type="submit" class="btn btn-black">ENTRAR AGORA</button>
            </form>
        </div>

        <div class="right">
            <h2>🌍 Fundo Social</h2>
            <p style="color:#666; margin-bottom: 30px;">Contribuição para valores globais.</p>
            
            <img src="https://b.stripecdn.com/docs-statics-srv/assets/payment-method-icons/cards_32.png" style="margin-bottom:20px;">
            <h1 style="color:#28a745; margin:0 0 20px 0;">R$ 50,00</h1>

            <form action="/create-checkout-session" method="POST">
                <button type="submit" class="btn btn-stripe">
                    Pagar com Stripe
                </button>
            </form>
        </div>
    </div>
</body>
</html>
"""

# --- HTML DO AUDIT (TELA VERDE/HACKER) ---
AUDIT_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Painel Audit</title>
<style>
    body { background: black; color: #0f0; font-family: monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .terminal { border: 2px solid #0f0; padding: 40px; width: 600px; box-shadow: 0 0 20px #0f0; text-align: left; }
    h1 { border-bottom: 1px dashed #0f0; padding-bottom: 10px; text-align: center; }
    .status { color: yellow; font-weight: bold; }
    .logout { display: block; text-align: center; margin-top: 30px; color: #fff; text-decoration: none; border: 1px solid #fff; padding: 10px; }
    .logout:hover { background: #fff; color: black; }
</style>
</head>
<body>
    <div class="terminal">
        <h1>MONEY LAYER AUDIT</h1>
        <p>> USUÁRIO DETECTADO: {{ user }}</p>
        <p>> STATUS DO SISTEMA: <span class="status">ONLINE</span></p>
        <p>> CONEXÃO BANCO DE DADOS: <span class="status">SECURE (SSL)</span></p>
        <p>> CONTROLE DE VALORES: <span class="status">SOCIAL INTEREST ACTIVE</span></p>
        <br>
        <p>=========================================</p>
        <p>Acesso liberado para operações globais.</p>
        <p>=========================================</p>
        
        <a href="/" class="logout">DESCONECTAR</a>
    </div>
</body>
</html>
"""

# --- ROTAS DO FLASK ---
@app.route('/')
def index():
    return render_template_string(HOME_HTML)

@app.route('/gerar_token', methods=['POST'])
def gerar_token():
    email = request.form.get('email')
    cpf = request.form.get('cpf')
    code = str(random.randint(100000, 999999))
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO user_sessions (cpf, email, token) VALUES (%s, %s, %s)", (cpf, email, code))
        conn.commit()
        cur.close()
        conn.close()
        # TELA DE SUCESSO DO CÓDIGO
        return f"""
        <body style='background:#222; text-align:center; color:white; font-family:sans-serif; padding-top:100px;'>
            <h1 style='color:#28a745'>CÓDIGO GERADO!</h1>
            <div style='font-size:80px; margin:20px; border:2px dashed #28a745; display:inline-block; padding:20px;'>{code}</div>
            <br><a href='/' style='color:white; font-size:20px;'>VOLTAR E ENTRAR</a>
        </body>
        """
    except Exception as e:
        return f"<h1>ERRO NO BANCO: {e}</h1>"

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    token = request.form.get('token')
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT token FROM user_sessions WHERE email = %s ORDER BY id DESC LIMIT 1", (email,))
        res = cur.fetchone()
        cur.close()
        conn.close()
        
        if res and res[0] == token:
            session['user'] = email
            # AQUI CARREGA O PAINEL HACKER
            return render_template_string(AUDIT_HTML, user=email)
        return "<h1>TOKEN INVÁLIDO</h1><a href='/'>Voltar</a>"
    except Exception as e:
        return f"Erro: {e}"

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            line_items=[{'price_data': {'currency': 'brl', 'product_data': {'name': 'Contribuição Social'}, 'unit_amount': 5000}, 'quantity': 1}],
            mode='payment',
            success_url=request.host_url + 'audit_redirect', # Ajuste técnico
            cancel_url=request.host_url,
        )
        return redirect(session.url, code=303)
    except Exception as e:
        return str(e)
        
# Rota extra para capturar o retorno do Stripe
@app.route('/audit_redirect')
def audit_redirect():
     return render_template_string(AUDIT_HTML, user="Contribuidor Global")

if __name__ == "__main__":
    # RODANDO NA PORTA 8081 PARA MUDAR O LINK E EVITAR CACHE
    app.run(host="0.0.0.0", port=8081, debug=True)
