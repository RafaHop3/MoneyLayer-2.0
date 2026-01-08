import os
import psycopg2
from flask import Flask, render_template
from flask_apscheduler import APScheduler
from scheduler_tasks import executar_distribuicao_social, processar_folha_pagamento

class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.config.from_object(Config())

# Inicializa o Agendador
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

DB_URL = os.environ.get('DATABASE_URL')

def get_total_social():
    try:
        conn = psycopg2.connect(DB_URL, sslmode='require')
        cur = conn.cursor()
        # Soma tudo que é do tipo SOCIAL no banco
        cur.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'SOCIAL'")
        total = cur.fetchone()[0]
        conn.close()
        return total if total else 0.0
    except:
        return 0.0

@scheduler.task('interval', id='social_job', seconds=60, misfire_grace_time=900)
def job_social():
    executar_distribuicao_social(app)

@app.route('/')
def index():
    # Busca o valor REAL do banco de dados
    valor_social = get_total_social()
    
    saldo_str = f"R$ {valor_social:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    return render_template('index.html', 
                           saldo_formatado=saldo_str, 
                           status_scheduler="Ativo e Gerando Valor 🚀")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
