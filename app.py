import os
import psycopg2
from flask import Flask, render_template
from flask_apscheduler import APScheduler
from scheduler_tasks import executar_distribuicao_social

class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

DB_URL = os.environ.get('DATABASE_URL')

def get_dados():
    try:
        conn = psycopg2.connect(DB_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'SOCIAL'")
        saldo = cur.fetchone()[0] or 0.0
        cur.execute("SELECT data_transacao, tipo, valor, descricao, destino FROM financeiro ORDER BY data_transacao DESC LIMIT 10")
        extrato = cur.fetchall()
        conn.close()
        return saldo, extrato
    except:
        return 0.0, []

@scheduler.task('interval', id='social_job', seconds=60)
def job_social():
    executar_distribuicao_social(app)

@app.route('/')
def index():
    saldo, extrato = get_dados()
    saldo_fmt = f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return render_template('index.html', saldo_formatado=saldo_fmt, extrato=extrato, status_scheduler="Ativo 🟢")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
