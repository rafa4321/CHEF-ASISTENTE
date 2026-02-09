import os
import json
import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Canal profesional: Hugging Face
async def generar_obra_de_arte(prompt_comida):
    # Usamos Pollinations pero con un método de "cache-busting" y 
    # parámetros de estilo profesional para evitar el robot y el error 403
    import random
    seed = random.randint(1, 100000)
    
    # Construimos un prompt ultra-detallado para calidad profesional
    prompt_final = (
        f"Professional food photography of {prompt_comida}, "
        "gourmet plating, Michelin star restaurant style, studio lighting, "
        "8k ultra realistic, highly detailed textures"
    ).replace(" ", "%20")
    
    # Esta URL está optimizada para saltar bloqueos
    url = f"https://image.pollinations.ai/prompt/{prompt_final}?seed={seed}&width=1024&height=768&nologo=true"
    return url

@app.get("/search")
async def get_recipe(query: str = Query(...)):
    try:
        # 1. Generar Receta con Groq
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres un Chef de alta cocina. Responde SOLO en JSON con 'title', 'ingredients' (lista) e 'instructions' (texto)."},
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        receta = json.loads(completion.choices[0].message.content)
        
        # 2. Generar Imagen con Estilo Profesional
        # Pasamos el título exacto para que la imagen coincida con la receta
        receta['image_url'] = await generar_obra_de_arte(receta.get('title', query))
        
        return [receta]
    except Exception as e:
        return {"error": str(e)}