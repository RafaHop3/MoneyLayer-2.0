import os

# Conteúdo da primeira parte (Imports, Config e Banco)
code = r'''import os
import stripe
import psycopg2
from flask import Flask, render_template, jsonify, request, redirect
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURAÇÕES ---
stripe.api_key = os.getenv("STRIPE_API_KEY")
DB_URL = os.getenv("DATABASE_URL")
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
'''

# Cria o arquivo app.py do zero ('w' = write/escrever)
with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Parte 1 gravada com sucesso!")