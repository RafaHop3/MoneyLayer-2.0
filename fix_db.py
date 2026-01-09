import os
import psycopg2

try:
    print("🔌 Conectando ao Neon...")
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    
    print("🔨 Adicionando coluna 'is_admin'...")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;")
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ SUCESSO! A coluna 'is_admin' foi criada.")
except Exception as e:
    print(f"❌ Erro: {e}")
