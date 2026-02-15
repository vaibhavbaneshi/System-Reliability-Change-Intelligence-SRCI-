import os
from fastapi import APIRouter
from app.ml.train_model import train_model

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL")

@router.post("/train")
def train():
    result = train_model(DATABASE_URL)
    return result