import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Permitir que Flutter (localhost) hable con Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REEMPLAZA ESTO CON TU CLAVE DE GROQ
client = Groq(api_key="TU_CLAVE_AQUÍ")

@app.get("/search")
async def search_recipe(query: str = Query(...)):
    # Filtro de seguridad para que solo acepte comida
    prompt = f"""
    Eres un Chef experto. Si el usuario pregunta por algo que NO es comida (como carros o herramientas), 
    di que solo sabes de cocina. Si es comida, genera una receta REAL para: {query}.
    Responde ÚNICAMENTE en este formato JSON:
    {{
      "title": "Nombre de la receta",
      "ingredients": ["1kg de algo", "2 tazas de otro"],
      "instructions": ["Paso 1...", "Paso 2..."],
      "description": "Explicación breve"
    }}
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"title": "Error", "ingredients": [], "instructions": [str(e)], "description": ""}