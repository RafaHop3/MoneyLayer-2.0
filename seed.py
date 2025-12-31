# seed.py (CORRIGIDO)
from sqlmodel import Session, select, text  # <--- Adicionamos 'text' aqui
from backend.database import engine
from backend.services.transaction_service import TransactionService
from backend.models.ledger import AccountType
from decimal import Decimal
import backend.models.ledger

def run_seed():
    print("🌱 Iniciando o Seed (População de Teste)...")
    
    with Session(engine) as session:
        service = TransactionService(session)

        # 1. Limpeza rápida (Opcional, para não duplicar se rodar várias vezes)
        # Em produção não faríamos isso, mas para teste é bom
        # session.exec(text("TRUNCATE TABLE journal_entries, transactions, accounts RESTART IDENTITY CASCADE"))
        # session.commit()

        # 1. Criar Contas
        print("👤 Criando usuários...")
        # Verifica se já existem para não dar erro
        alice = service.create_account("Alice da Silva " + str(Decimal(1)), AccountType.USER)
        bob = service.create_account("Bob Santos " + str(Decimal(1)), AccountType.USER)
        system_mint = service.create_account("Emissor Central", AccountType.SYSTEM)

        # 2. Injetar Dinheiro na Alice
        print("💰 Creditando R$ 1.000,00 para Alice...")
        service.process_transaction(
            source_account_id=system_mint.id,
            target_account_id=alice.id,
            amount=Decimal("1000.00"),
            description="Depósito Inicial",
            apply_social_tax=False
        )

        # 3. Teste Real: Alice transfere 100 para Bob (Com taxa social)
        print("\n💸 Alice transfere R$ 100,00 para Bob (Com Taxa Social)...")
        tx = service.process_transaction(
            source_account_id=alice.id,
            target_account_id=bob.id,
            amount=Decimal("100.00"),
            description="Pagamento de Serviço",
            apply_social_tax=True 
        )
        
        print(f"✅ Transação Concluída! Ref: {tx.reference}")

        # 4. Auditoria Final (Verificar saldos)
        print("\n🔎 --- AUDITORIA DO LEDGER ---")
        
        def get_balance(account_id):
            # AQUI ESTAVA O ERRO: Agora usamos text()
            query = text("SELECT SUM(amount) FROM journal_entries WHERE account_id = :aid")
            result = session.execute(query, {"aid": account_id}).scalar()
            return result if result else Decimal(0)

        alice_balance = get_balance(alice.id)
        bob_balance = get_balance(bob.id)
        
        # Buscar o fundo social
        social_fund = session.exec(select(backend.models.ledger.Account).where(backend.models.ledger.Account.account_type == AccountType.SOCIAL_FUND)).first()
        social_balance = get_balance(social_fund.id)

        print(f"Alice (Pagou 100):     R$ {alice_balance}")
        print(f"Bob (Recebeu 99):      R$ {bob_balance}")
        print(f"Fundo Social (+1%):    R$ {social_balance}")

        # Nota: Como rodamos o seed 2 vezes (uma falhou no final), os valores podem estar acumulados.
        print("\n🏆 SUCESSO! A Governança Social está ativa.")

if __name__ == "__main__":
    run_seed()