from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import os 
import json 
from dotenv import load_dotenv 

# --- 1. CONFIGURACIÓN DE RUTAS ABSOLUTAS ---
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_file_path))
env_path = os.path.join(project_root, '.env')

if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    print(f"✅ SISTEMA: Archivo .env cargado desde {env_path}")
else:
    print(f"⚠️ SISTEMA: No se encontró .env en {env_path}")

GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# --- 2. INICIALIZACIÓN GEMINI ---
try:
    from google import genai
    if not GEMINI_KEY:
        GEMINI_CLIENT = None
        print("🔴 ERROR: GEMINI_API_KEY vacía en el archivo .env")
    else:
        GEMINI_CLIENT = genai.Client(api_key=GEMINI_KEY)
        print("✅ SISTEMA: Cliente IA inicializado.")
except Exception as e:
    GEMINI_CLIENT = None
    print(f"🔴 ERROR CRÍTICO: {e}")

app = FastAPI()

# --- 3. CORS MIDDLEWARE (Esencial para Flutter Web) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "online", "key_loaded": GEMINI_KEY is not None}

@app.get("/search")
async def search_recipes(query: str):
    if not GEMINI_CLIENT:
        raise HTTPException(status_code=500, detail="Error de configuración API Key.")

    # --- 4. PROMPT REFORZADO ---
    system_prompt = """
    Actúa como Chef Senior y Nutricionista.
    REGLAS ESTRICTAS:
    1. Responde ÚNICAMENTE con una lista JSON válida [].
    2. No incluyas texto explicativo, ni etiquetas markdown como ```json.
    3. Incluye: title, description, ingredients (con pesos), instructions, prep_time, calories, macros (objeto), estimated_price, diet_type, nutritional_notes.
    """
    
    try:
        response = GEMINI_CLIENT.models.generate_content(
            model='gemini-2.0-flash', 
            contents=[system_prompt, f"Receta para: {query}"]
        )
        
        # --- 5. LIMPIEZA DE RESPUESTA ---
        # Elimina posibles bloques de código que la IA suele añadir
        text_response = response.text.strip()
        if text_response.startswith("```"):
            text_response = text_response.replace("```json", "").replace("```", "").strip()
        
        return json.loads(text_response)

    except Exception as e:
        print(f"❌ Error interno: {e}")
        raise HTTPException(status_code=500, detail=str(e))