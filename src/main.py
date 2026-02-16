import os
import json
import httpx
import base64
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def generar_imagen_ia(descripcion_plato):
    """Llama a Hugging Face para crear una imagen real del plato"""
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    
    # Prompt optimizado para que la comida se vea real
    prompt = f"Gourmet professional food photography of {descripcion_plato}, high resolution, cinematic lighting, 8k, delicious."
    
    try:
        async with httpx.AsyncClient() as ac:
            response = await ac.post(api_url, headers=headers, json={"inputs": prompt}, timeout=60.0)
            if response.status_code == 200:
                # Convertimos el binario de la imagen a Base64 para enviarlo al celular
                return f"data:image/jpeg;base64,{base64.b64encode(response.content).decode('utf-8')}"
    except Exception as e:
        print(f"Error generando imagen: {e}")
    # Si falla, enviamos una de repuesto (pero no la de la ensalada)
    return "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1000"

@app.get("/search")
async def buscar_receta(query: str = Query(...)):
    try:
        system_prompt = """
        Eres un Chef Profesional. Responde en JSON. 
        'ins' debe ser una LISTA de al menos 6 pasos muy detallados.
        'ing' debe incluir medidas exactas.
        """
        
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        data = json.loads(completion.choices[0].message.content)
        
        # AQUÍ ESTÁ EL CAMBIO: Generamos la imagen para CADA búsqueda
        foto_real = await generar_imagen_ia(data.get("title", query))

        return [{
            "title": data.get("title", query).upper(),
            "kcal": data.get("kcal", "0"),
            "proteina": data.get("prot", "0g"),
            "ingredients": data.get("ing", []),
            "instructions": data.get("ins", []), # Lista de pasos
            "image_url": foto_real
        }]
    except Exception as e:
        return [{"title": "Error", "instructions": [str(e)]}]