from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv  # <--- CERTIFIQUE-SE QUE ESTA LINHA ESTÁ LÁ
import os

# Importar os modelos para que o SQLModel saiba que eles existem
from backend.models import ledger 

# 1. Carrega as senhas
load_dotenv()
database_url = os.getenv("DATABASE_URL")

# 2. Cria o motor de conexão
# O echo=True mostra o SQL no terminal
engine = create_engine(database_url, echo=True)

# 3. Função para criar as tabelas
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# 4. Função para dependência de sessão
def get_session():
    with Session(engine) as session:
        yield session

if __name__ == "__main__":
    print("⏳ Criando tabelas no banco de dados...")
    create_db_and_tables()
    print("✅ Tabelas criadas com sucesso!")