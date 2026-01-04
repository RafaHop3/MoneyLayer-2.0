from pydantic import BaseModel, Field, field_validator, model_validator

class GlobalControls(BaseModel):
    # Regras de Negócio (Taxas)
    max_transaction_fee: float = Field(..., gt=0, description="Taxa máxima permitida (%)")
    social_redistribution_rate: float = Field(..., ge=0, le=100, description="Doação para comunidade (%)")
    
    # Regras de Sustentabilidade Interna (Salários)
    min_employee_salary: float = Field(..., gt=0, description="Menor salário pago na empresa")
    ceo_salary: float = Field(..., gt=0, description="Salário do CEO")

    # 1. Validador da Taxa (Individual)
    @field_validator('max_transaction_fee')
    @classmethod
    def check_fee_cap(cls, v: float) -> float:
        if v > 5.0:
            raise ValueError('A taxa viola a missão social (Limite: 5%)')
        return v

    # 2. Validador da Equidade (Comparativo)
    @model_validator(mode='after')
    def check_salary_equity(self):
        # A regra: CEO não pode ganhar mais que 10x a base
        limit = self.min_employee_salary * 10
        
        if self.ceo_salary > limit:
            raise ValueError(
                f'Violação de Equidade: O CEO ganha {self.ceo_salary}, mas o limite é {limit} '
                f'(10x o menor salário de {self.min_employee_salary}).'
            )
        return self

class MoneyLayerStatus(BaseModel):
    status: str
    service: str
    social_mission: str
    version: str
    governance: GlobalControls