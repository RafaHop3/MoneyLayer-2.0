import os

# O código completo e corrigido do app.py
code = r'''import os
import stripe
import psycopg2
from flask import Flask, render_template, jsonify, request, redirect
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURAÇÕES ---
stripe.api_key = os.getenv("STRIPE_API_KEY")
DB_URL = os.getenv("DATABASE_URL")
# Garante que usa a URL certa (com ou sem 2-0)
DOMAIN = os.getenv("RENDER_EXTERNAL_URL", "https://moneylayer-2-0.onrender.com")

# --- BANCO DE DADOS ---
def get_db_connection():
    if not DB_URL:
        return None
    return psycopg2.connect(DB_URL)

def init_db():
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

with app.app_context():
    init_db()

# --- ROTAS ---
@app.route("/")
def home():
    saldo = 0.0
    extrato = []
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            # Pega as últimas 10 transações
            cur.execute("SELECT created_at, type, amount, description FROM transactions ORDER BY created_at DESC LIMIT 10")
            extrato = cur.fetchall()
            
            # Calcula saldo social
            cur.execute("SELECT SUM(amount) FROM transactions WHERE type='SOCIAL'")
            row = cur.fetchone()
            if row and row[0]:
                saldo = row[0]
            cur.close()
            conn.close()
    except Exception as e:
        print(f"Erro banco: {e}")

    return render_template("index.html", saldo_formatado=f"R$ {saldo:.2f}", extrato=extrato)

@app.route("/api/status")
def status():
    return jsonify({
        "status": "active",
        "service": "Money Layer",
        "social_mission": "Financial access for all",
        "version": "MVP 1.0"
    })

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                "price_data": {
                    "currency": "brl",
                    "product_data": {"name": "Doação MoneyLayer"},
                    "unit_amount": 1000,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=DOMAIN,
            cancel_url=DOMAIN,
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return str(e)

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        valor_total = session.get("amount_total", 0) / 100.0
        valor_social = valor_total * 0.05
        
        try:
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO transactions (amount, type, description) VALUES (%s, %s, %s)", (valor_total, "ENTRADA", "Venda via Stripe"))
                cur.execute("INSERT INTO transactions (amount, type, description) VALUES (%s, %s, %s)", (valor_social, "SOCIAL", "Repasse 5%"))
                conn.commit()
                cur.close()
                conn.close()
                print(f"💰 Pagamento: {valor_total} | Social: {valor_social}")
        except Exception as e:
            print(f"Erro DB: {e}")

    return "Success", 200

if __name__ == "__main__":
    app.run(port=3000)
'''

with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ SUCESSO: Cérebro do MoneyLayer (app.py) restaurado!")
