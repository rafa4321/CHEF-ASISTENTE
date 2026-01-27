import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Permitimos que tu Flutter Web se conecte sin bloqueos de seguridad
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Coloca aquí tu API KEY de Groq
client = Groq(api_key="TU_CLAVE_DE_GROQ_AQUI")

@app.get("/search")
async def search_recipe(query: str = Query(...)):
    # Prompt optimizado para obtener solo datos de cocina
    prompt = f"""
    Eres un Chef profesional. Genera una receta detallada para: {query}.
    Responde ÚNICAMENTE en formato JSON con esta estructura exacta:
    {{
      "title": "Nombre de la receta",
      "ingredients": ["ingrediente 1 con cantidad", "ingrediente 2 con cantidad"],
      "instructions": ["Paso 1 detallado", "Paso 2 detallado"],
      "description": "Breve descripción del plato."
    }}
    Si el usuario pide algo que no es comida, indica en el 'title' que solo eres un Chef.
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        # Cargamos el JSON de la IA. FastAPI se encarga de enviarlo como UTF-8
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"title": "Error", "ingredients": [], "instructions": [str(e)]}