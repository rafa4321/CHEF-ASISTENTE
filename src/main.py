import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Configuración de CORS para permitir la conexión desde Flutter Web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
async def search_recipe(query: str):
    # Paso 1: Verificar la API Key en el entorno
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        return {"title": "Error: GROQ_API_KEY no configurada en Render", "ingredients": [], "instructions": []}

    try:
        client = Groq(api_key=api_key)
        prompt = f"Genera una receta de {query} en JSON con campos: title, time, difficulty, ingredients (lista), instructions (lista)."
        
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        data = json.loads(completion.choices[0].message.content)
        return {
            "title": data.get("title", f"Receta de {query}"),
            "time": data.get("time", "N/A"),
            "difficulty": data.get("difficulty", "N/A"),
            "ingredients": list(data.get("ingredients", [])),
            "instructions": list(data.get("instructions", []))
        }
    except Exception as e:
        # Esto te dirá el error real (ej: API Key inválida) en el navegador
        return {
            "title": "Error de IA", 
            "detalle": str(e),
            "ingredients": [], 
            "instructions": []
        }

if __name__ == "__main__":
    import uvicorn
    # Puerto dinámico para Render
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)