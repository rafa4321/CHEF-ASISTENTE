import sys
import io
import os
import json

# Parche de emergencia para forzar UTF-8 en el sistema
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Render leerá GROQ_API_KEY de las variables de entorno
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.get("/search")
async def search_recipe(query: str = Query(...)):
    prompt = f"Genera una receta de {query} en JSON con esta estructura: {{'title': 'string', 'ingredients': [], 'instructions': []}}. Responde solo el JSON."
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        # Cargamos el JSON y FastAPI lo enviará como UTF-8
        receta = json.loads(completion.choices[0].message.content)
        return receta
    except Exception as e:
        return {"title": "Error", "ingredients": [], "instructions": [str(e)]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)