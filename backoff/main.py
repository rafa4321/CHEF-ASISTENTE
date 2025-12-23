from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import os 
import json 
from dotenv import load_dotenv 

# Carga la clave API desde el archivo .env
load_dotenv() 

try:
    from google import genai 
    GEMINI_KEY = os.getenv("GEMINI_API_KEY") 
    # Inicialización del cliente con la clave del entorno
    GEMINI_CLIENT = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None
    if GEMINI_CLIENT:
        print("✅ Backend Activo: Modo Chef & Nutricionista Avanzado.")
except Exception as e:
    GEMINI_CLIENT = None
    print(f"🔴 Error de configuración: {e}")

app = FastAPI()

# Configuración de CORS para permitir la conexión desde Flutter Web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# Estructura de datos completa para nutrición y costos
class RecipeOption(BaseModel):
    title: str
    description: str
    ingredients: List[str]
    instructions: List[str]
    prep_time: str
    calories: str
    macros: Dict[str, str]
    estimated_price: str
    diet_type: str
    nutritional_notes: str

@app.get("/search")
async def search_recipes(query: str):
    if not GEMINI_CLIENT:
        raise HTTPException(status_code=500, detail="Falta la GEMINI_API_KEY en el archivo .env")

    # Prompt diseñado para extraer datos culinarios, nutricionales y financieros
    prompt = f"""
    Eres un Chef Senior y Nutricionista Certificado. Procesa la solicitud: "{query}".
    
    Debes generar una respuesta profesional que incluya:
    1. Ingredientes con PESOS exactos (g, kg, ml) y PRECIOS estimados en USD.
    2. Información nutricional: Calorías totales y desglose de Macronutrientes.
    3. Adecuación para dietas (Keto, Vegana, Celíaca, para diabéticos, etc.).
    4. Instrucciones de preparación paso a paso.

    Responde ÚNICAMENTE con este formato JSON (una lista con un objeto):
    [
        {{
            "title": "Nombre del Plato",
            "description": "Resumen del perfil de sabor y beneficios nutricionales",
            "ingredients": ["200g de Salmón ($4.50)", "150g de Espárragos ($1.20)"],
            "instructions": ["Paso 1: Precalentar...", "Paso 2: Sazonar..."],
            "prep_time": "25 minutos",
            "calories": "380 kcal",
            "macros": {{"proteinas": "35g", "carbohidratos": "8g", "grasas": "22g"}},
            "estimated_price": "$5.70 USD aprox.",
            "diet_type": "Keto / Paleo / Gluten-Free",
            "nutritional_notes": "Rico en Omega-3 y fibra. Bajo en sodio."
        }}
    ]
    """
    
    try:
        response = GEMINI_CLIENT.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt
        )
        # Limpieza por si la IA añade bloques de código markdown
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"Error IA: {e}")
        raise HTTPException(status_code=500, detail="Error al generar la receta técnica.")