import os
import json
import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def obtener_imagen_segmind(prompt_comida):
    # URL del modelo estándar de Segmind
    url = "https://api.segmind.com/v1/sdxl1.0-txt2img"
    api_key = os.getenv("SEGMIND_API_KEY")
    
    # Payload ultra-simplificado para evitar Error 406
    payload = {
        "prompt": f"Professional food photography of {prompt_comida}, 8k, appetizing",
        "samples": 1,
        "base64": False
    }
    headers = {'x-api-key': api_key}
    
    async with httpx.AsyncClient() as ac:
        try:
            # Aumentamos el timeout por si la generación es lenta
            response = await ac.post(url, json=payload, headers=headers, timeout=30.0)
            print(f"DEBUG SEGMIND: Status {response.status_code}")
            
            if response.status_code == 200:
                return response.json().get('url')
            
            # Si falla Segmind, usamos un respaldo visual temporal para que no veas el icono roto
            return f"https://placehold.co/1024x768?text={prompt_comida.replace(' ', '+')}"
        except Exception as e:
            print(f"DEBUG ERROR: {e}")
            return None

@app.get("/search")
async def get_recipe(query: str = Query(...)):
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Chef. Responde SOLO JSON: {'title': str, 'ingredients': list, 'instructions': str}."},
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        receta = json.loads(completion.choices[0].message.content)
        
        # Llamada a la imagen optimizada
        receta['image_url'] = await obtener_imagen_segmind(receta.get('title', query))
        return [receta]
    except Exception as e:
        return {"error": str(e)}