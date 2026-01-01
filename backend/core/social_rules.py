from decimal import Decimal
from .money_safety import transaction_guard

class SocialConfig:
    # Regras de Negócio
    LIMIT_HIGH_VALUE = Decimal('1000.00')
    TAXA_PADRAO = Decimal('0.01')      # 1%
    TAXA_PROGRESSIVA = Decimal('0.05') # 5%

@transaction_guard
def calcular_distribuicao(valor_bruto: Decimal) -> dict:
    """
    Função Pura: Recebe um valor e retorna a distribuição justa
    protegida pelo @transaction_guard.
    """
    if valor_bruto >= SocialConfig.LIMIT_HIGH_VALUE:
        taxa = SocialConfig.TAXA_PROGRESSIVA
    else:
        taxa = SocialConfig.TAXA_PADRAO
    
    social = valor_bruto * taxa
    destino = valor_bruto - social
    
    return {
        "valor_original": valor_bruto,
        "taxa_aplicada": taxa,
        "social": social,
        "destino": destino
    }