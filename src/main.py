import os
import json
import httpx # Usamos httpx que es más moderno y robusto
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def obtener_imagen_segmind(prompt_comida):
    url = "https://api.segmind.com/v1/sdxl1.0-txt2img"
    api_key = os.getenv("SEGMIND_API_KEY")
    
    payload = {
        "prompt": f"Gourmet food photo of {prompt_comida}, professional lighting, 8k",
        "base64": False
    }
    headers = {'x-api-key': api_key}
    
    async with httpx.AsyncClient() as ac:
        try:
            response = await ac.post(url, json=payload, headers=headers, timeout=20.0)
            print(f"DEBUG SEGMIND: Status {response.status_code}") # Ver esto en logs de Render
            if response.status_code == 200:
                return response.json().get('url')
            return "https://via.placeholder.com/1024x768.png?text=Error+en+API+Segmind"
        except Exception as e:
            print(f"DEBUG ERROR: {e}")
            return None

@app.get("/search")
async def get_recipe(query: str = Query(...)):
    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Chef. Responde JSON: {'title': str, 'ingredients': list, 'instructions': str}."},
            {"role": "user", "content": f"Receta de {query}"}
        ],
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"}
    )
    receta = json.loads(completion.choices[0].message.content)
    # Obtenemos la imagen
    receta['image_url'] = await obtener_imagen_segmind(receta.get('title', query))
    return [receta]