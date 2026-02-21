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
    
    # CAMBIO CATEGÓRICO: Usamos 'gemini-pro', el modelo más compatible del mundo.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"Genera una receta de cocina para: {query}. "
                    "Responde exclusivamente en formato JSON con esta estructura exacta: "
                    '{"title": "Nombre", "kcal": "valor", "proteina": "valor", '
                    '"ingredients": ["item1", "item2"], "instructions": ["paso1", "paso2"], '
                    '"img_prompt": "foto gourmet de {query}"}'
                )
            }]
        }]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=30.0)
            data = response.json()
            
            # Si Gemini-Pro no está disponible, el error será capturado aquí con detalle
            if "error" in data:
                return [{"error": f"Google dice: {data['error']['message']}"}]

            texto_ia = data['candidates'][0]['content']['parts'][0]['text']
            
            # Limpieza de JSON
            texto_ia = texto_ia.replace("```json", "").replace("```", "").strip()
            receta = json.loads(texto_ia)
            
            img_url = f"https://image.pollinations.ai/prompt/{receta.get('img_prompt', query).replace(' ', '%20')}?model=flux&nologo=true"

            return [{
                "title": receta.get('title', query).upper(),
                "kcal": f"{receta.get('kcal', '0')} Kcal",
                "proteina": f"{receta.get('proteina', '0')} Prot",
                "ingredients": receta.get('ingredients', []),
                "instructions": receta.get('instructions', []),
                "image_url": img_url
            }]
        except Exception as e:
            return [{"error": f"Error técnico: {str(e)}"}]

@app.get("/")
async def root():
    return {"status": "online", "message": "API Chef v4.0 (Gemini Pro)"}