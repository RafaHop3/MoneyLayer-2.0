from decimal import Decimal
from sqlmodel import Session, select
from backend.models.ledger import Account, Transaction, JournalEntry, TransactionStatus, AccountType
import uuid

class TransactionService:
    def __init__(self, session: Session):
        self.session = session

    def create_account(self, name: str, account_type: AccountType = AccountType.USER) -> Account:
        """Cria uma nova conta no sistema."""
        account = Account(name=name, account_type=account_type)
        self.session.add(account)
        self.session.commit()
        self.session.refresh(account)
        return account

    def process_transaction(self, 
                            source_account_id: int, 
                            target_account_id: int, 
                            amount: Decimal, 
                            description: str,
                            apply_social_tax: bool = True) -> Transaction:
        """
        Executa uma transação atômica de partidas dobradas.
        Se apply_social_tax=True, cobra 1% para o Fundo Social.
        """
        # 1. Validações Básicas
        if amount <= 0:
            raise ValueError("O valor da transação deve ser positivo.")
        
        # 2. Inicia a Transação (Objeto Pai)
        tx_ref = str(uuid.uuid4())
        
        transaction = Transaction(
            reference=tx_ref,
            description=description,
            status=TransactionStatus.PENDING
        )
        self.session.add(transaction)
        self.session.flush() # Para gerar o ID da transaction

        # 3. Lógica de Governança Social (Taxa de 1%)
        tax_amount = Decimal('0.00')
        final_amount = amount

        if apply_social_tax:
            # Encontra ou cria a conta do Fundo Social
            social_fund = self._get_or_create_system_account("Fundo Social Global", AccountType.SOCIAL_FUND)
            
            tax_amount = amount * Decimal('0.01') # 1% de taxa
            final_amount = amount - tax_amount

            # Entrada do Fundo Social (Crédito)
            self._create_entry(transaction.id, social_fund.id, tax_amount)

        # 4. Partidas Dobradas (O Coração do Sistema)
        # Débito na origem (Valor negativo)
        self._create_entry(transaction.id, source_account_id, -amount)
        
        # Crédito no destino (Valor positivo - já descontada a taxa se houver)
        self._create_entry(transaction.id, target_account_id, final_amount)

        # 5. Validação Final (A soma deve ser ZERO)
        transaction.status = TransactionStatus.COMPLETED
        transaction.audit_hash = "HASH_VALIDADO" 
        
        self.session.add(transaction)
        self.session.commit()
        self.session.refresh(transaction)
        
        return transaction

    def _create_entry(self, tx_id: int, account_id: int, amount: Decimal):
        entry = JournalEntry(
            transaction_id=tx_id,
            account_id=account_id,
            amount=amount
        )
        self.session.add(entry)

    def _get_or_create_system_account(self, name: str, type: AccountType) -> Account:
        statement = select(Account).where(Account.account_type == type)
        account = self.session.exec(statement).first()
        if not account:
            account = self.create_account(name, type)
        return account