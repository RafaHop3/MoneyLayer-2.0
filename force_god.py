import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
YOUR_GOD_CPF = "86001396000"

with engine.connect() as conn:
    # Força o seu CPF a ser GOD e garante que ele seja o ID 1 se possível
    conn.execute(text("UPDATE users SET is_god = True WHERE cpf = :cpf"), {"cpf": YOUR_GOD_CPF})
    conn.commit()
    print(f"SUCESSO: O CPF {YOUR_GOD_CPF} agora tem poderes SUPREMOS no banco de dados.")

