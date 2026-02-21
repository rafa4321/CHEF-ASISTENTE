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
    
    # LA FÓRMULA: Usamos v1 (Estable) con el path completo del modelo
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"Genera una receta de cocina para: {query}. "
                    "Responde estrictamente en formato JSON con esta estructura exacta: "
                    '{"title": "Nombre", "kcal": "valor", "proteina": "valor", '
                    '"ingredients": ["item1", "item2"], "instructions": ["paso1", "paso2"], '
                    '"img_prompt": "comida gourmet de {query}"}'
                )
            }]
        }],
        "generationConfig": {
            "temperature": 1,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 8192,
            "responseMimeType": "application/json",
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            
            # Si hay error, lo mostramos detallado para no adivinar más
            if response.status_code != 200:
                return [{"error": f"Error {response.status_code}", "detalle": response.json()}]
            
            data = response.json()
            texto_ia = data['candidates'][0]['content']['parts'][0]['text']
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
            return [{"error": f"Error de conexión: {str(e)}"}]

@app.get("/")
async def root():
    return {"status": "online", "engine": "Gemini 1.5 Flash (V1)"}