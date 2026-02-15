import os
import json
import httpx
import base64
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/search")
async def verify_step_1(query: str = Query(...)):
    try:
        # Instrucción de precisión absoluta
        system_prompt = """
        Eres un Chef Profesional. Responde ÚNICAMENTE con un JSON válido.
        ESTRUCTURA REQUERIDA (NO FALLAR):
        {
          "title": "Nombre del plato",
          "description": "Descripción breve",
          "ingredients": ["lista", "de", "strings"],
          "steps": ["paso 1", "paso 2", "paso 3"],
          "nutrition": {"calories": "0", "protein": "0g", "carbs": "0g", "fat": "0g"}
        }
        """
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        receta = json.loads(completion.choices[0].message.content)
        
        # VALIDACIÓN MILIMÉTRICA: Si la IA falla, el código corrige el formato antes de enviar
        if isinstance(receta.get('steps'), str): receta['steps'] = [receta['steps']]
        if isinstance(receta.get('ingredients'), str): receta['ingredients'] = [receta['ingredients']]
        
        # Imagen de prueba (usaremos una fija para no gastar intentos de IA en este paso)
        receta['image_url'] = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"
        
        return [receta]
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)