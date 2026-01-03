import sys
import os

# Adiciona o diretório atual ao caminho do Python
sys.path.append(os.getcwd())

# Tenta importar da estrutura padrão
try:
    from backend.database import SessionLocal, engine, Base
    print("✅ Conectado ao banco via: backend/database.py")
except ImportError:
    # Fallback caso você tenha movido para core
    from backend.core.database import SessionLocal, engine, Base
    print("✅ Conectado ao banco via: backend/core/database.py")

from backend.core.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def run_seed():
    print("🌱 Iniciando Seed do Money Layer 2.0...")
    
    # Cria as tabelas (users, transactions)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Verifica se o Admin já existe
        existing_user = db.query(User).filter(User.email == "admin@moneylayer.com").first()
        
        if existing_user:
            print("⚠️ Usuário Admin já existe (ID: 1).")
        else:
            admin_user = User(
                email="admin@moneylayer.com",
                hashed_password=pwd_context.hash("123456"),
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("✅ Usuário Admin criado com sucesso (ID: 1).")
            
    except Exception as e:
        print(f"❌ Erro ao inserir dados: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()