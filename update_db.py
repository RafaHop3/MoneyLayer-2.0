cat <<EOF > update_db.py
import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERRO: DATABASE_URL vazia. Rode o comando export primeiro!")
else:
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        # Adiciona a coluna admin se ela nao existir
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;")
        conn.commit()
        conn.close()
        print("✅ Banco Atualizado com Sucesso (Coluna Admin Criada)!")
    except Exception as e:
        print(f"Erro no banco: {e}")
EOF