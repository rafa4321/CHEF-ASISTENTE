import os
import httpx
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
async def buscar_receta(query: str = Query(...)):
    api_key = os.getenv("GOOGLE_API_KEY")
    # URL directa de la API de Google, sin usar librerías intermedias
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Genera una receta para: {query}. Responde solo en JSON con: title, kcal, proteina, ingredients (lista), instructions (lista), img_prompt."
            }]
        }]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            data = response.json()
            
            # Extraemos el texto de la respuesta de Google
            texto_ia = data['candidates'][0]['content']['parts'][0]['text']
            
            # Limpiamos el JSON por si viene con ```json
            texto_ia = texto_ia.replace("```json", "").replace("```", "").strip()
            receta = json.loads(texto_ia)
            
            img_url = f"[https://image.pollinations.ai/prompt/](https://image.pollinations.ai/prompt/){receta.get('img_prompt', query).replace(' ', '%20')}?model=flux&nologo=true"

            return [{
                "title": receta.get('title', query).upper(),
                "kcal": receta.get('kcal', 'N/A'),
                "proteina": receta.get('proteina', 'N/A'),
                "ingredients": receta.get('ingredients', []),
                "instructions": receta.get('instructions', []),
                "image_url": img_url
            }]
        except Exception as e:
            return [{"error": f"Error crítico: {str(e)}", "detalles": data if 'data' in locals() else "No hay respuesta de Google"}]

@app.get("/")
async def root():
    return {"status": "online", "message": "Chef Asistente API v3.0"}