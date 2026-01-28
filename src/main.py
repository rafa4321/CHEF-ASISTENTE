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
    # Personalidad de Chef de alto nivel para Google Play
    system_message = (
        "Eres un Chef de prestigio internacional. Solo respondes sobre gastronomía. "
        "Si la consulta no es culinaria, responde estrictamente: {'error': 'Lo siento, como Chef experto solo puedo asistirte con recetas.'}"
    )
    
    user_prompt = (
        f"Genera una receta detallada para: {query}. "
        "Responde en JSON con estas llaves exactas: "
        "'title', 'description', 'time', 'difficulty', 'ingredients', 'instructions', 'chef_tip'."
    )

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_message}, {"role": "user", "content": user_prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        receta = json.loads(completion.choices[0].message.content)
        # UTF-8 garantizado para evitar errores de tildes
        return JSONResponse(content=receta, media_type="application/json; charset=utf-8")
    except Exception:
        return JSONResponse(content={"error": "Error en la cocina digital."}, status_code=500)