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
    
    # La URL más estable a nivel mundial en febrero 2026
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    
    # Payload ultra-compatible (sin generationConfig complejo para evitar el error 400)
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"Genera una receta para: {query}. "
                    "Responde exclusivamente en este formato JSON: "
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
            
            # Si Google responde con error, lo exponemos directamente para saber qué pasa
            if "error" in data:
                return [{"error": f"Google AI Studio dice: {data['error']['message']}"}]

            # Extraemos y limpiamos el texto
            texto_raw = data['candidates'][0]['content']['parts'][0]['text']
            # Quitamos posibles etiquetas ```json si la IA las pone
            texto_limpio = texto_raw.replace("```json", "").replace("```", "").strip()
            
            receta = json.loads(texto_limpio)
            
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
            return [{"error": f"Fallo interno: {str(e)}"}]

@app.get("/")
async def root():
    return {"status": "online", "message": "Chef API conectada"}