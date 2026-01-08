import os
import json
import stripe
import psycopg2
from flask import Flask, render_template, request, jsonify
from flask_apscheduler import APScheduler
from scheduler_tasks import executar_distribuicao_social

# --- CONFIGURAÇÃO ---
class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.config.from_object(Config())

# Inicializa o Robô (Scheduler)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Configuração do Banco e Stripe
DB_URL = os.environ.get('DATABASE_URL')
# A chave virá das variáveis de ambiente do Render depois
stripe.api_key = os.environ.get('STRIPE_API_KEY') 
ENDPOINT_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

def get_db_connection():
    return psycopg2.connect(DB_URL, sslmode='require')

# --- FUNÇÕES DE BANCO DE DADOS ---
def registrar_pagamento_real(valor_bruto, origem):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. Registra a Entrada Real
        cur.execute("""
            INSERT INTO financeiro (tipo, valor, descricao, destino) 
            VALUES ('ENTRADA', %s, %s, 'Caixa Empresa')
        """, (valor_bruto, f"Venda via Stripe ({origem})"))
        
        # 2. Calcula o Social (5%)
        # Futuramente isso virá da tabela de regras, por enquanto fixo para performance
        valor_social = float(valor_bruto) * 0.05
        
        # 3. Separa o Dinheiro Social
        cur.execute("""
            INSERT INTO financeiro (tipo, valor, descricao, destino) 
            VALUES ('SOCIAL', %s, 'Aplicação Automática 5%%', 'Fundo Social')
        """, (valor_social,))
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"💰 SUCESSO: Pagamento de R$ {valor_bruto} processado. R$ {valor_social} foi para social.")
        return True
    except Exception as e:
        print(f"❌ ERRO AO GRAVAR NO BANCO: {e}")
        return False

def get_dados_auditoria():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'SOCIAL'")
        saldo = cur.fetchone()[0] or 0.0
        cur.execute("SELECT data_transacao, tipo, valor, descricao, destino FROM financeiro ORDER BY data_transacao DESC LIMIT 10")
        extrato = cur.fetchall()
        conn.close()
        return saldo, extrato
    except:
        return 0.0, []

# --- ROTAS ---

@app.route('/')
def index():
    saldo, extrato = get_dados_auditoria()
    saldo_fmt = f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return render_template('index.html', saldo_formatado=saldo_fmt, extrato=extrato, status_scheduler="Aguardando Vendas 💳")

# AQUI É ONDE O STRIPE BATE NA PORTA
@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    event = None

    try:
        # Verifica se foi mesmo o Stripe que mandou (Segurança)
        if ENDPOINT_SECRET:
            event = stripe.Webhook.construct_event(payload, sig_header, ENDPOINT_SECRET)
        else:
            # Modo Dev sem validação de assinatura (apenas para teste rápido)
            data = json.loads(payload)
            event = data

    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400

    # Lógica de Recebimento
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Stripe envia em centavos (ex: 1000 = R$ 10,00), precisamos dividir
        amount_total = session.get('amount_total', 0) / 100 
        customer_email = session.get('customer_details', {}).get('email', 'anonimo')
        
        registrar_pagamento_real(amount_total, customer_email)

    return jsonify(success=True)

# Mantemos o scheduler rodando para simular custos operacionais ou outras tarefas
@scheduler.task('interval', id='social_job', seconds=60)
def job_social():
    executar_distribuicao_social(app)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
