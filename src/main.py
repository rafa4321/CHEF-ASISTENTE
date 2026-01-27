import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from dotenv import load_dotenv

# 1. Cargamos variables de entorno (API Key)
load_dotenv()

app = FastAPI(title="Chef Asistente API")

# 2. CONFIGURACIÓN CRÍTICA DE CORS 
# Esto permite que tu App de Flutter (localhost) se conecte a Render sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las conexiones
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, etc.
    allow_headers=["*"],
)

# 3. Inicializamos el cliente de IA (Groq)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/")
def read_root():
    return {"status": "Chef Online", "message": "Listo para cocinar"}

@app.get("/search")
async def search_recipe(query: str):
    try:
        # 4. Prompt para asegurar que la IA siempre responda en JSON
        prompt = f"""
        Eres un Chef experto. Genera una receta detallada para: {query}.
        Responde ÚNICAMENTE en formato JSON con esta estructura exacta:
        {{
            "title": "Nombre de la receta",
            "description": "Breve descripción",
            "ingredients": ["ingrediente 1", "ingrediente 2"],
            "instructions": ["paso 1", "paso 2"]
        }}
        Si el usuario pide algo que no es comida (como un 'bloque de motor'), 
        responde que no puedes cocinar eso con humor.
        """

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )

        # 5. Procesamos la respuesta de la IA
        receta_raw = chat_completion.choices[0].message.content
        return json.loads(receta_raw)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Usamos el puerto que asigne Render o el 8000 por defecto
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)