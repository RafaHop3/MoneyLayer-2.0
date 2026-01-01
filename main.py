from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from decimal import Decimal, InvalidOperation
import threading
import time

# -------------------------------------------------------------------------
# LÓGICA DE NEGÓCIO BLINDADA
# -------------------------------------------------------------------------
class SocialMoneyLayer:
    def __init__(self, initial_fund="1000.00"):
        self._lock = threading.Lock()
        self._global_social_fund = Decimal(initial_fund)
        self._audit_trail = []

    def get_balance(self):
        with self._lock:
            return self._global_social_fund

    def distribute_social_value(self, amount_str, purpose):
        try:
            amount = Decimal(amount_str)
        except InvalidOperation:
            raise ValueError("Formato de número inválido.")

        if amount <= 0:
            raise ValueError("O valor deve ser positivo.")

        with self._lock:
            if self._global_social_fund >= amount:
                # Simula latência
                time.sleep(0.001) 
                self._global_social_fund -= amount
                
                log = {
                    "action": "DISTRIBUTE",
                    "amount": str(amount),
                    "purpose": purpose,
                    "status": "SUCCESS",
                    "timestamp": time.time()
                }
                self._audit_trail.append(log)
                return True, log
            else:
                return False, {"error": "Fundos insuficientes"}

    def get_audit_logs(self):
        return self._audit_trail

# -------------------------------------------------------------------------
# APLICAÇÃO WEB (FASTAPI)
# -------------------------------------------------------------------------

app = FastAPI(title="MoneyLayer 2.0 - Social Core")

money_layer = SocialMoneyLayer()

class DistributeRequest(BaseModel):
    amount: str
    purpose: str

@app.get("/")
def read_root():
    return {"status": "Online", "message": "MoneyLayer 2.0 Operacional"}

@app.get("/balance")
def get_balance():
    return {"global_social_fund": str(money_layer.get_balance())}

@app.post("/distribute")
def distribute_funds(request: DistributeRequest):
    try:
        success, info = money_layer.distribute_social_value(request.amount, request.purpose)
        if success:
            return {"status": "Transferência Realizada", "details": info}
        else:
            raise HTTPException(status_code=400, detail="Saldo Insuficiente na Camada Global")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.get("/audit")
def get_audit():
    return {"logs": money_layer.get_audit_logs()}
