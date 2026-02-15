import os
import json
import httpx
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
async def get_recipe_fixed(query: str = Query(...)):
    try:
        system_prompt = """
        Eres un Chef Pro. Responde ÚNICAMENTE en JSON con esta estructura exacta:
        {
          "title": "Nombre del Plato | Cal: 500 - Prot: 30g", 
          "description": "Breve reseña",
          "ingredients": ["1 taza de arroz", "2 huevos"],
          "steps": ["Paso 1: Cocinar arroz", "Paso 2: Freír huevos"],
          "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"
        }
        Nota: Incluye la nutrición básica resumida directamente en el 'title' para que aparezca en la franja del nombre.
        'steps' DEBE ser una lista de frases, NO un párrafo largo.
        """

        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        data = json.loads(completion.choices[0].message.content)
        
        # Forzar formato de lista para evitar el error de la imagen 8de5a7.jpg
        if isinstance(data.get('steps'), str):
            data['steps'] = [s.strip() for s in data['steps'].split('.') if s.strip()]
            
        return [data]
    except Exception as e:
        return [{"error": str(e)}]