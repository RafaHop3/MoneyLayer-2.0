import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    # Se nao tiver URL (teste local sem render), usa um valor padrao ou avisa
    print("⚠️  ATENÇÃO: DATABASE_URL não encontrada. Se estiver local, verifique a conexão.")
    # Para facilitar seu teste local no Codespaces, podemos tentar conectar direto se tiver credenciais
    # Mas idealmente, vamos assumir que o ambiente já tem a URL ou falhar.
else:
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Cria a tabela de usuarios
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                nickname VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(200) NOT NULL
            );
        """)

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Tabela de Usuários (Login) criada com sucesso!")
    except Exception as e:
        print(f"Erro ao conectar: {e}")
