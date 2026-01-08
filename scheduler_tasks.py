import os
import psycopg2
from datetime import datetime
import random

# Pega a URL segura do ambiente do Render
DB_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DB_URL, sslmode='require')

def executar_distribuicao_social(app):
    with app.app_context():
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # 1. Simula uma Receita (ENTRADA) para a empresa ter o que dividir
            faturamento = random.uniform(1000.00, 5000.00)
            cur.execute("""
                INSERT INTO financeiro (tipo, valor, descricao, destino)
                VALUES ('ENTRADA', %s, 'Faturamento Automático', 'Caixa Empresa')
            """, (faturamento,))
            
            # 2. Busca a Regra Social Ativa (ex: 5%)
            cur.execute("SELECT porcentagem FROM regras_sociais WHERE ativo = TRUE LIMIT 1")
            regra = cur.fetchone()
            porcentagem = regra[0] if regra else 5.0
            
            # 3. Calcula e Aplica o Social (SOCIAL)
            valor_social = faturamento * (float(porcentagem) / 100)
            
            cur.execute("""
                INSERT INTO financeiro (tipo, valor, descricao, destino)
                VALUES ('SOCIAL', %s, 'Distribuição Automática', 'Fundo Social')
            """, (valor_social,))
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"[{datetime.now()}] 💰 FATURAMENTO: R$ {faturamento:.2f} | ❤️ SOCIAL GERADO: R$ {valor_social:.2f}")
            
        except Exception as e:
            print(f"[{datetime.now()}] ❌ ERRO NO SCHEDULER: {e}")

def processar_folha_pagamento(app):
    # Lógica futura para salários
    pass
