import unittest
import threading
import time
from decimal import Decimal, getcontext

# Configuração de precisão financeira global
getcontext().prec = 28

# -------------------------------------------------------------------------
# MOCK DA SUA LÓGICA (Exemplo de como sua classe deve se comportar)
# Substitua ou adapte esta classe pela sua implementação real
# -------------------------------------------------------------------------
class SocialMoneyLayer:
    def __init__(self, initial_fund="0.00"):
        # O Lock é essencial para evitar Race Conditions em variáveis globais
        self._lock = threading.Lock()
        self._global_social_fund = Decimal(initial_fund)
        self._audit_trail = []

    def get_balance(self):
        with self._lock:
            return self._global_social_fund

    def distribute_social_value(self, amount_str, purpose):
        """
        Distribui valor para um propósito social.
        Retorna True se sucesso, False se saldo insuficiente.
        """
        amount = Decimal(amount_str)
        
        if amount <= 0:
            raise ValueError("O valor deve ser positivo.")

        with self._lock:
            if self._global_social_fund >= amount:
                # Simulação de processamento (latência de rede/banco)
                time.sleep(0.001) 
                
                # A mágica: subtração atômica
                self._global_social_fund -= amount
                
                # Registro de Auditoria (Crucial para o social)
                self._audit_trail.append({
                    "action": "DISTRIBUTE",
                    "amount": str(amount),
                    "purpose": purpose,
                    "status": "SUCCESS"
                })
                return True
            else:
                self._audit_trail.append({
                    "action": "DISTRIBUTE_FAIL",
                    "amount": str(amount),
                    "purpose": purpose,
                    "reason": "INSUFFICIENT_FUNDS"
                })
                return False

    def add_global_funding(self, amount_str, source):
        amount = Decimal(amount_str)
        if amount <= 0:
            raise ValueError("O aporte deve ser positivo.")
            
        with self._lock:
            self._global_social_fund += amount
            self._audit_trail.append({
                "action": "FUNDING",
                "amount": str(amount),
                "source": source
            })

    def get_audit_logs(self):
        return self._audit_trail


# -------------------------------------------------------------------------
# O TESTE "GRAND FINALE" (A Suíte de Validação Robusta)
# -------------------------------------------------------------------------
class TestGrandFinale(unittest.TestCase):

    def setUp(self):
        # Inicia cada teste com um fundo limpo de 1000.00
        self.money_layer = SocialMoneyLayer(initial_fund="1000.00")

    def test_01_precision_decimal(self):
        """Garante que não estamos perdendo centavos (Erro de float)"""
        print("\n[Teste 01] Verificando precisão Decimal...")
        
        # Adiciona 0.1 + 0.1 + 0.1 dez vezes. Se fosse float, isso daria 0.99999...
        for _ in range(10):
            self.money_layer.add_global_funding("0.10", "Micro Donation")
        
        balance = self.money_layer.get_balance()
        # 1000.00 + 1.00 deve ser EXATAMENTE 1001.00
        self.assertEqual(balance, Decimal("1001.00"))

    def test_02_concurrency_stress(self):
        """
        O TESTE DE FOGO: 100 threads tentando sacar ao mesmo tempo.
        Se o sistema não tiver Thread Safety, o saldo final estará errado.
        """
        print("[Teste 02] Estresse de Concorrência (Race Conditions)...")
        
        initial_balance = self.money_layer.get_balance() # 1000.00
        withdrawal_amount = "10.00"
        num_threads = 100 # 100 * 10.00 = 1000.00 (Deve zerar a conta)

        def worker():
            self.money_layer.distribute_social_value(withdrawal_amount, "Stress Test")

        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        final_balance = self.money_layer.get_balance()
        print(f"   Saldo Inicial: {initial_balance}")
        print(f"   Saldo Final:   {final_balance}")
        
        self.assertEqual(final_balance, Decimal("0.00"), 
                         "ALERTA CRÍTICO: O saldo não zerou corretamente! Há uma falha de concorrência.")

    def test_03_audit_integrity(self):
        """Garante que o dinheiro não se move sem deixar rastro social"""
        print("[Teste 03] Verificando Integridade da Auditoria...")
        
        self.money_layer.distribute_social_value("50.00", "Bolsa Educação")
        logs = self.money_layer.get_audit_logs()
        
        last_entry = logs[-1]
        self.assertEqual(last_entry['purpose'], "Bolsa Educação")
        self.assertEqual(last_entry['amount'], "50.00")
        self.assertEqual(last_entry['status'], "SUCCESS")

    def test_04_prevent_negative_values(self):
        """Garante que ninguém pode injetar dívida ou sacar valores negativos"""
        print("[Teste 04] Bloqueio de valores negativos...")
        
        with self.assertRaises(ValueError):
            self.money_layer.add_global_funding("-100.00", "Hacker Attempt")
            
        with self.assertRaises(ValueError):
            self.money_layer.distribute_social_value("-50.00", "Exploit Attempt")

    def test_05_insufficient_funds_protection(self):
        """Garante que não é possível gastar o que não tem"""
        print("[Teste 05] Proteção de Saldo Insuficiente...")
        
        # Tenta sacar 2000 (temos apenas 1000)
        result = self.money_layer.distribute_social_value("2000.00", "Projeto Gigante")
        
        self.assertFalse(result)
        self.assertEqual(self.money_layer.get_balance(), Decimal("1000.00")) # Saldo inalterado

if __name__ == '__main__':
    unittest.main()