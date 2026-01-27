import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Configuración de CORS para permitir la conexión desde Flutter
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
    # Prompt de ingeniería para obligar a la IA a ser un Chef y filtrar otros temas
    prompt = f"""
    Eres un Chef profesional de clase mundial.
    Tu tarea es generar una receta real, detallada y deliciosa para: {query}.
    
    REGLAS CRÍTICAS:
    1. Si la búsqueda NO está relacionada con comida, ingredientes o cocina (ej. 'caja de velocidades', 'computadoras'), responde con un JSON que diga que solo sabes de cocina.
    2. Los ingredientes deben incluir cantidades reales (ej. '250g de harina').
    3. Las instrucciones deben ser pasos lógicos y numerados.
    4. Responde ÚNICAMENTE en formato JSON con esta estructura exacta:
    {{
      "title": "Nombre de la receta",
      "ingredients": ["ingrediente 1", "ingrediente 2"],
      "instructions": ["paso 1", "paso 2"],
      "description": "Breve descripción"
    }}
    """

    try:
        # Llamada real a la API de Groq
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        
        # Extraemos y cargamos el JSON de la respuesta
        recipe_data = json.loads(chat_completion.choices[0].message.content)
        return recipe_data

    except Exception as e:
        return {
            "title": "Error en la cocina",
            "ingredients": ["No pudimos obtener los ingredientes"],
            "instructions": [f"Detalle del error: {str(e)}"],
            "description": "Hubo un problema al conectar con la IA."
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)