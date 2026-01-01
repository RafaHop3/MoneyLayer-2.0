from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/status")
def auth_status():
    return {"status": "Auth module active"}
