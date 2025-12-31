# seed.py (Versão Final - Com Senhas)
from sqlmodel import Session, select
from backend.database import engine
from backend.services.transaction_service import TransactionService
from backend.models.ledger import AccountType, Account
from backend.security import get_password_hash
from decimal import Decimal
import backend.models.ledger

def run_seed():
    print("🌱 Iniciando o Seed Seguro (Com Login)...")
    
    with Session(engine) as session:
        service = TransactionService(session)

        # Função para criar usuário com senha corretamente
        def create_user_with_password(name, username, password):
            # Verifica se já existe
            existing = session.exec(select(Account).where(Account.username == username)).first()
            if existing:
                print(f"   -> Usuário {username} já existe.")
                return existing
            
            # Cria conta direto no modelo para passar o hash da senha
            account = Account(
                name=name, 
                username=username,
                hashed_password=get_password_hash(password), # Criptografa a senha!
                account_type=AccountType.USER
            )
            session.add(account)
            session.commit()
            session.refresh(account)
            print(f"   -> Criado: {username} (ID: {account.id})")
            return account

        print("👤 Criando usuários...")
        # Criamos Alice e Bob com senha '123456'
        alice = create_user_with_password("Alice da Silva", "alice", "123456")
        bob = create_user_with_password("Bob Santos", "bob", "123456")
        
        # Cria o emissor (Sistema)
        system_mint = Account(
            name="Emissor Central", 
            username="system_mint", 
            hashed_password=get_password_hash("sys_key_x99"),
            account_type=AccountType.SYSTEM
        )
        
        # Salva o sistema se não existir
        if not session.exec(select(Account).where(Account.account_type == AccountType.SYSTEM)).first():
            session.add(system_mint)
            session.commit()
            session.refresh(system_mint)
        else:
             system_mint = session.exec(select(Account).where(Account.account_type == AccountType.SYSTEM)).first()

        # Injetar Dinheiro na Alice (1000 reais)
        print("💰 Creditando R$ 1.000,00 para Alice...")
        service.process_transaction(
            source_account_id=system_mint.id,
            target_account_id=alice.id,
            amount=Decimal("1000.00"),
            description="Depósito Inicial Seed",
            apply_social_tax=False
        )

        print("\n✅ Seed Concluído! \nLogin: 'alice' \nSenha: '123456'")

if __name__ == "__main__":
    run_seed()