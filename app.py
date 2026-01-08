import os
import psycopg2
from flask import Flask, render_template
from flask_apscheduler import APScheduler
from scheduler_tasks import executar_distribuicao_social, processar_folha_pagamento

class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

DB_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DB_URL, sslmode='require')

def get_dados_financeiros():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. Pega o Saldo Total Social
        cur.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'SOCIAL'")
        resultado_saldo = cur.fetchone()
        saldo = resultado_saldo[0] if resultado_saldo[0] else 0.0
        
        # 2. Pega as últimas 10 movimentações (O Extrato)
        cur.execute("""
            SELECT data_transacao, tipo, valor, descricao, destino 
            FROM financeiro 
            ORDER BY data_transacao DESC 
            LIMIT 10
        """)
        extrato = cur.fetchall()
        
        conn.close()
        return saldo, extrato
    except Exception as e:
        print(f"Erro no banco: {e}")
        return 0.0, []

@scheduler.task('interval', id='social_job', seconds=60, misfire_grace_time=900)
def job_social():
    executar_distribuicao_social(app)

@app.route('/')
def index():
    saldo_social, lista_extrato = get_dados_financeiros()
    
    saldo_str = f"R$ {saldo_social:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    return render_template('index.html', 
                           saldo_formatado=saldo_str, 
                           extrato=lista_extrato,
                           status_scheduler="Sistema Operante 🟢")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
