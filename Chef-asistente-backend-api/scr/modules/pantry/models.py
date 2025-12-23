# También en souschef-backend-api/src/modules/pantry/models.py
# (Usado por FastAPI para la validación de la API)

from pydantic import BaseModel
from typing import Optional
from datetime import date
from uuid import UUID

# Esquema de ENTRADA (Datos que envía el Frontend al crear/actualizar)
class PantryIngredientInput(BaseModel):
    name: str
    quantity: float
    unit: str
    expiration_date: Optional[date] = None
    price_per_unit: Optional[float] = 0.0

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Leche",
                "quantity": 1.5,
                "unit": "litros",
                "expiration_date": "2025-12-30"
            }
        }

# Esquema de SALIDA (Datos que el Backend envía al Frontend)
class PantryIngredientOutput(PantryIngredientInput):
    ingredient_id: UUID
    user_id: UUID

    class Config:
        # Permite mapear campos de ORM/DB a Pydantic
        from_attributes = True