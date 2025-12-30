from sqlmodel import SQLModel, Session, create_engine
import os
from dotenv import load_dotenv

# 1. Carrega as senhas
load_dotenv()
database_url = os.getenv("DATABASE_URL")

# 2. Cria o motor de conexão
# O echo=True mostra o SQL no terminal (bom para ver acontecendo)
engine = create_engine(database_url, echo=True)

# 3. Função para criar as tabelas (Rode este arquivo uma vez!)
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# 4. Função que as rotas vão usar para pegar uma sessão do banco
def get_session():
    with Session(engine) as session:
        yield session

if __name__ == "__main__":
    print("⏳ Criando tabelas no banco de dados...")
    create_db_and_tables()
    print("✅ Tabelas criadas com sucesso!")