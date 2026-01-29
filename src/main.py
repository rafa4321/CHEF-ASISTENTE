import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Configuración de CORS: Permite que tu app de Flutter Web se comunique con el servidor
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# PASO 1: Conexión con la variable de entorno de Render
# Asegúrate de que en Render la llave se llame exactamente GROQ_API_KEY
api_key_env = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key_env)

@app.get("/search")
async def search_recipe(query: str):
    # Prompt optimizado para recibir un JSON estricto
    prompt = f"Genera una receta de {query} en JSON con campos: title, time, difficulty, ingredients (lista), instructions (lista)."
    
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        # Procesamos la respuesta de la IA
        data = json.loads(completion.choices[0].message.content)
        
        # Retornamos los datos asegurando que ingredientes e instrucciones sean listas
        return {
            "title": str(data.get("title", f"Receta de {query}")),
            "time": str(data.get("time", "N/A")),
            "difficulty": str(data.get("difficulty", "N/A")),
            "ingredients": list(data.get("ingredients", [])),
            "instructions": list(data.get("instructions", []))
        }
    except Exception as e:
        # Si la API Key falla o la IA no responde, enviamos este error controlado
        print(f"Error detallado: {e}")
        return {
            "title": "Error de IA",
            "ingredients": ["Verifica la API Key en Render"],
            "instructions": ["Error en la comunicación con Groq"],
            "time": "N/A",
            "difficulty": "N/A"
        }

if __name__ == "__main__":
    import uvicorn
    # Render asigna un puerto automáticamente mediante la variable PORT
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)