import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from groq import Groq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.get("/search")
async def search_recipe(query: str = Query(...)):
    # Filtro de contenido y personalidad de Chef profesional
    system_message = (
        "Eres un Chef estrella Michelin. Tu misión es dar recetas detalladas, claras y profesionales. "
        "REGLA CRÍTICA: Si el usuario pregunta por algo que NO sea gastronómico (ej. motores, mecánica, política, electrónica), "
        "responde únicamente: {'error': 'Lo siento, como Chef experto solo puedo asistirte con recetas y temas culinarios.'}"
    )
    
    user_prompt = (
        f"Proporciona una receta detallada para: {query}. "
        "La respuesta debe ser un objeto JSON con: "
        "'title' (nombre del plato), "
        "'description' (una breve explicación de qué es el plato y su origen), "
        "'ingredients' (lista de strings con cantidades exactas), "
        "'instructions' (pasos numerados detallados y explicativos)."
    )

    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        datos = json.loads(completion.choices[0].message.content)
        # Forzamos la codificación correcta para evitar errores de tildes
        return JSONResponse(content=datos, media_type="application/json; charset=utf-8")
        
    except Exception as e:
        return JSONResponse(content={"error": "Hubo un problema al conectar con la cocina."}, status_code=500)