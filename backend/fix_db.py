import os
import sys
from dotenv import load_dotenv

# Garante que o Python encontre a pasta backend
sys.path.append(os.getcwd())

print("📂 Carregando variáveis de ambiente...")
load_dotenv()

# Verifica credenciais
url = os.getenv("DATABASE_URL")
if not url:
    # Tenta carregar forçado
    load_dotenv(os.path.join(os.getcwd(), ".env"))
    url = os.getenv("DATABASE_URL")

if not url:
    print("❌ ERRO: .env não encontrado ou vazio.")
    sys.exit(1)

print("✅ Credenciais OK. Conectando ao Banco...")

# Importa o banco e os modelos
from sqlmodel import SQLModel
from backend.database import engine
import backend.models.ledger 

def fix_database():
    print("🧨 Apagando tabelas antigas...")
    try:
        SQLModel.metadata.drop_all(engine)
    except Exception as e:
        print(f"Aviso (pode ignorar se for o primeiro reset): {e}")

    print("✨ Criando tabelas NOVAS (com username/senha)...")
    SQLModel.metadata.create_all(engine)
    print("🏆 BANCO RESETADO COM SUCESSO!")

if __name__ == "__main__":
    fix_database()