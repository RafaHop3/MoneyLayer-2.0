import secrets
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Importações do projeto
from backend.routers import auth, transactions, social
from backend.database import get_db
from backend.core.models import User

# Configuração de Senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 1. Inicializa a API SEM as docs automáticas (para não ficarem públicas)
app = FastAPI(
    title="MoneyLayer 2.0",
    docs_url=None,       # Desativa /docs público
    redoc_url=None,      # Desativa /redoc público
    openapi_url=None     # Desativa o JSON público
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SEGURANÇA DO SWAGGER ---
security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    # Busca o usuário no banco
    user = db.query(User).filter(User.email == credentials.username).first()
    
    # Verifica se usuário existe e a senha bate
    if not user or not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais Incorretas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user.email

# 2. Rota Protegida para o Swagger UI (/docs)
@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(get_current_username)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="MoneyLayer 2.0 Docs")

# 3. Rota Protegida para o JSON (/openapi.json)
@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(username: str = Depends(get_current_username)):
    return get_openapi(title="MoneyLayer 2.0", version="2.0", routes=app.routes)

# --- ROTAS NORMAIS ---
app.include_router(auth.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(social.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "MoneyLayer 2.0 - Secure Mode 🔒"}
