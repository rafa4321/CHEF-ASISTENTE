import os
import json
import httpx
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
    
    # ACTUALIZACIÓN: Usamos Gemini 2.5 Flash (visto en tu lista de modelos)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"Genera una receta para: {query}. "
                    "Responde estrictamente en formato JSON plano (sin markdown) con esta estructura: "
                    '{"title": "Nombre", "kcal": "valor", "proteina": "valor", '
                    '"ingredients": ["item 1", "item 2"], "instructions": ["paso 1", "paso 2"], '
                    '"img_prompt": "foto gourmet de {query}"}'
                )
            }]
        }]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=30.0)
            data = response.json()
            
            if "error" in data:
                return [{"error": f"Google 2.5 dice: {data['error']['message']}"}]

            texto_ia = data['candidates'][0]['content']['parts'][0]['text']
            # Limpiamos el texto por si la IA se pone creativa con el formato
            texto_ia = texto_ia.replace("```json", "").replace("```", "").strip()
            
            receta = json.loads(texto_ia)
            
            # Generamos la imagen con Pollinations (Modelo Flux)
            img_url = f"https://image.pollinations.ai/prompt/{receta.get('img_prompt', query).replace(' ', '%20')}?model=flux&nologo=true"

            return [{
                "title": receta.get('title', query).upper(),
                "kcal": receta.get('kcal', 'N/A'),
                "proteina": receta.get('proteina', 'N/A'),
                "ingredients": receta.get('ingredients', []),
                "instructions": receta.get('instructions', []),
                "image_url": img_url
            }]
        except Exception as e:
            return [{"error": f"Error del servidor: {str(e)}"}]

@app.get("/")
async def root():
    return {"status": "online", "model": "Gemini 2.5 Flash (Pago activado)"}