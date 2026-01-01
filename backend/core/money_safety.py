import functools
from decimal import Decimal, getcontext

# Configuração Global
getcontext().prec = 28

class MoneySystemError(Exception):
    """Exceção base para erros financeiros."""
    pass

# --- FERRAMENTA 1: CIRCUIT BREAKER (Guardião de Fluxo) ---
class CircuitBreaker:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CircuitBreaker, cls).__new__(cls)
        return cls._instance

    def __init__(self, limite_global='100000.00'):
        # Singleton: Garante que o limite é global para toda a aplicação
        if not hasattr(self, 'initialized'):
            self.limite = Decimal(limite_global)
            self.acumulado = Decimal('0.00')
            self.is_open = False
            self.initialized = True

    def check_flux(self, valor: Decimal):
        if self.is_open:
            raise MoneySystemError("⛔ SAFETY LOCK: Sistema travado por segurança.")
        
        previsao = self.acumulado + valor
        if previsao > self.limite:
            self.is_open = True
            raise MoneySystemError(f"🚨 ALERTA: Volume {valor} estouraria o limite global de {self.limite}!")
        
        # Se passou, computa (em produção real, isso seria resetado periodicamente)
        self.acumulado += valor
        return True

# Instância global para ser importada
global_circuit_breaker = CircuitBreaker()

# --- FERRAMENTA 2: GATEKEEPER (Auditor Matemático) ---
def transaction_guard(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 1. Busca o valor monetário nos argumentos (assume que é o primeiro Decimal encontrado)
        valor_transacao = None
        for arg in args:
            if isinstance(arg, float):
                 raise MoneySystemError("CRÍTICO: Uso de Float proibido.")
            if isinstance(arg, Decimal) and valor_transacao is None:
                valor_transacao = arg
        
        if valor_transacao is None:
             # Se não achou Decimal, talvez esteja dentro de um objeto, mas por segurança passamos
             pass 
        else:
            # 2. Verifica Circuit Breaker
            global_circuit_breaker.check_flux(valor_transacao)

        # 3. Executa
        result = func(*args, **kwargs)
        
        # 4. Auditoria de Saída (Se retornar dicionário com divisão)
        if isinstance(result, dict) and 'social' in result and 'destino' in result:
            total = result['social'] + result['destino']
            if isinstance(valor_transacao, Decimal) and total != valor_transacao:
                 raise MoneySystemError(f"FALHA DE INTEGRIDADE: Entrou {valor_transacao}, Saiu {total}")

        return result
    return wrapper