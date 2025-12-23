# src/routes/pantry_routes.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

# Define el router que será incluido en main.py
router = APIRouter(
    prefix="/pantry",
    tags=["Pantry"]
)

# Definición del Modelo de Ingrediente (similar al de Flutter)
class Ingredient(BaseModel):
    name: str
    quantity: float
    unit: str
    expiration_date: str # Usamos string aquí para simplificar la transferencia

# --- SIMULACIÓN DE BASE DE DATOS ---
# Usamos una lista simple para simular la base de datos (DB) antes de conectar MongoDB
FAKE_PANTRY_DB = []


@router.post("/add")
async def add_ingredient(ingredient: Ingredient):
    # Lógica de prueba: Añadir ingrediente a la DB simulada
    FAKE_PANTRY_DB.append(ingredient.model_dump())
    print(f"✅ Backend: Ingrediente añadido: {ingredient.name}. Total: {len(FAKE_PANTRY_DB)}")
    
    # Respuesta que Flutter espera (200 OK)
    return {"message": "Ingrediente añadido con éxito"}

@router.get("/list", response_model=List[Ingredient])
async def list_pantry():
    # Lógica de prueba: Retorna la lista de ingredientes
    print(f"✅ Backend: Solicitud de lista recibida. Ingredientes: {len(FAKE_PANTRY_DB)}")
    return FAKE_PANTRY_DB

@router.delete("/clear")
async def clear_pantry():
    # Lógica para limpiar la DB (útil para pruebas)
    FAKE_PANTRY_DB.clear()
    return {"message": "Despensa limpiada"}