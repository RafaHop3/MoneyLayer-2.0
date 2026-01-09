import os
import stripe
import psycopg2
from flask import Flask, render_template, jsonify, request, redirect
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURAÇÕES ---
# Pega as chaves do ambiente (que definimos no Render)
stripe.api_key = os.getenv('STRIPE_API_KEY')
DB_URL = os.getenv('DATABASE_URL')
DOMAIN = os.getenv('RENDER_EXTERNAL_URL', 'http://localhost:10000')

# --- BANCO DE DADOS ---
def get_db_connection():
    if not DB_URL:
        return None
    return psycopg2.connect(DB_URL)

def init_db():
    """Cria a tabela se ela nao existir"""
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    amount REAL NOT NULL,
                    type TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("✅ Banco de dados inicializado!")
    except Exception as e:
        print(f"⚠️ Erro ao iniciar banco: {e}")

# Inicializa o banco ao ligar o app
with app.app_context():
    init_db()

# --- ROTAS ---

@app.route('/')
def home():
    """Rota Principal: Mostra o Painel Visual"""
    saldo = 0.0
    extrato = []
    
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            
            # 1. Busca as últimas 10 transações
            cur.execute("SELECT created_at, type, amount, description FROM transactions ORDER BY created_at DESC LIMIT 10")
            extrato = cur.fetchall()
            
            # 2. Calcula o Saldo Social (Soma de tudo que é 'SOCIAL')
            cur.execute("SELECT SUM(amount) FROM transactions WHERE type='SOCIAL'")
            resultado = cur.fetchone()
            if resultado and resultado[0]:
                saldo = resultado[0]
                
            cur.close()
            conn.close()
    except Exception as e:
        print(f"Erro ao ler banco: {e}")

    # Renderiza o HTML passando os dados
    return render_template('index.html', 
                         saldo_formatado=f"R$ {saldo:.2f}", 
                         extrato=extrato)

@app.route('/api/status')
def status():
    """A rota JSON que você gostou (agora fica aqui)"""
    return jsonify({
        "status": "active",
        "service": "Money Layer",
        "social_mission": "Financial access for all",
        "version": "MVP 1.0"
    })

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Cria o pagamento no Stripe"""
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'brl',
                    'product_data': {'name': 'Doação MoneyLayer'},
                    'unit_amount': 1000, # R$ 10.00 (em centavos)
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=DOMAIN + '/?sucesso=true',
            cancel_url=DOMAIN + '/?cancelado=true',
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return str(e)

# --- WEBHOOK (Onde a mágica dos 5% acontece) ---
@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        valor_total = session.get('amount_total', 0) / 100.0 # Converte centavos para reais
        
        # AQUI É A REGRA DE OURO: 5% Social
        valor_social = valor_total * 0.05
        
        try:
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                
                # Registra a Venda
                cur.execute("INSERT INTO transactions (amount, type, description) VALUES (%s, %s, %s)",
                            (valor_total, 'ENTRADA', 'Venda via Stripe'))
                
                # Registra o Repasse Social Automático
                cur.execute("INSERT INTO transactions (amount, type, description) VALUES (%s, %s, %s)",
                            (valor_social, 'SOCIAL', 'Repasse Automático 5%'))
                
                conn.commit()
                cur.close()
                conn.close()
                print(f"💰 Pagamento Processado: R$ {valor_total} | Social: R$ {valor_social}")
        except Exception as e:
            print(f"Erro ao gravar no banco: {e}")

    return 'Success', 200

if __name__ == '__main__':
    # Roda localmente
    app.run(port=3000)
