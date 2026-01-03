# reset.py
import os
from dotenv import load_dotenv

# 1. Força o carregamento do .env antes de qualquer coisa
print(f"📂 Diretório atual: {os.getcwd()}")
if os.path.exists(".env"):
    print("✅ Arquivo .env encontrado! Carregando variáveis...")
    load_dotenv()
else:
    print("❌ ERRO CRÍTICO: Arquivo .env não encontrado na raiz!")
    exit(1)

# 2. Verifica se a URL carregou
db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("❌ ERRO: DATABASE_URL está vazia. Verifique seu arquivo .env.")
    exit(1)

# 3. Agora sim importa o backend (com a certeza que a URL existe)
try:
    from backend.database import engine
    from sqlmodel import SQLModel
    
    print("🗑️  Iniciando limpeza do banco de dados (DROP ALL)...")
    SQLModel.metadata.drop_all(engine)
    print("✨ Sucesso! O banco de dados está limpo e pronto para a nova estrutura.")

except Exception as e:
    print(f"❌ Ocorreu um erro durante o reset: {e}")