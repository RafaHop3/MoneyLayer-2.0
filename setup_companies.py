import os
import psycopg2

try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()

    print("🏗️ Criando tabela de Empresas...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            name VARCHAR(100) NOT NULL,
            tax_id VARCHAR(20),  -- CNPJ/CPF
            company_type VARCHAR(20), -- MEI, LTDA, Startup
            balance DECIMAL(10, 2) DEFAULT 0.00
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Sucesso! Tabela 'companies' pronta para uso.")
except Exception as e:
    print(f"❌ Erro: {e}")
