import os
import json
import httpx
import base64
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Arreglamos el error de CORS (image_d69a23.png)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def generar_imagen_elite(nombre_plato):
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    
    # Prompt optimizado para realismo extremo (Paso 2)
    prompt = f"Professional 8k food photography of {nombre_plato}, gourmet presentation, highly detailed, soft studio lighting, white background."
    
    try:
        async with httpx.AsyncClient() as ac:
            response = await ac.post(api_url, headers=headers, json={"inputs": prompt}, timeout=60.0)
            if response.status_code == 200:
                img_base64 = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/jpeg;base64,{img_base64}"
    except:
        pass
    
    # Fallback si falla el token (evita fotos rotas)
    return "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&q=80&w=1000"

@app.get("/search")
async def get_premium_recipe(query: str = Query(...)):
    try:
        system_prompt = """
        Eres un Chef Michelin. Responde ÚNICAMENTE en JSON.
        'ingredients' y 'steps' DEBEN SER LISTAS (no texto largo).
        'nutrition' debe ser un objeto con cal, protein, carbs, fat.
        """

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Receta profesional para: {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        receta = json.loads(completion.choices[0].message.content)
        
        # Inyectamos la foto generada por IA
        receta['image_url'] = await generar_imagen_elite(receta.get('title', query))
        
        # Normalizamos nombres para tu Flutter (compatibilidad total)
        resultado = {
            "title": receta.get("title", query),
            "description": receta.get("description", ""),
            "ingredients": receta.get("ingredients", []),
            "steps": receta.get("steps", []),
            "nutrition": receta.get("nutrition", {})
        }
        
        return [resultado]
        
    except Exception as e:
        return [{"error": str(e)}]