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
    
    # ENDPOINT ESTABLE: v1beta es el que mejor soporta JSON estructurado actualmente
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    
    # Payload simplificado (Sin campos que den error 400)
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"Genera una receta para: {query}. "
                    "Responde SOLO con un objeto JSON (sin markdown, sin texto extra) con esta estructura: "
                    '{"title": "Nombre", "kcal": "valor", "proteina": "valor", '
                    '"ingredients": ["item1"], "instructions": ["paso1"], '
                    '"img_prompt": "foto de {query}"}'
                )
            }]
        }]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            data = response.json()
            
            # Verificación de errores de Google
            if "error" in data:
                return [{"error": f"Error de Google: {data['error']['message']}"}]

            # Extraemos el texto y limpiamos CUALQUIER residuo de Markdown
            texto_ia = data['candidates'][0]['content']['parts'][0]['text']
            texto_ia = texto_ia.replace("```json", "").replace("```", "").strip()
            
            receta = json.loads(texto_ia)
            
            # Generación de imagen
            img_url = f"https://image.pollinations.ai/prompt/{receta.get('img_prompt', query).replace(' ', '%20')}?model=flux&nologo=true"

            return [{
                "title": receta.get('title', query).upper(),
                "kcal": receta.get('kcal', '0'),
                "proteina": receta.get('proteina', '0'),
                "ingredients": receta.get('ingredients', []),
                "instructions": receta.get('instructions', []),
                "image_url": img_url
            }]
        except Exception as e:
            return [{"error": f"Error en el servidor: {str(e)}"}]

@app.get("/")
async def root():
    return {"status": "online", "model": "Gemini 1.5 Flash Final"}