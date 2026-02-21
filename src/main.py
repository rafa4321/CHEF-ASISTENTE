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
    
    # LA FÓRMULA DE AI STUDIO:
    # 1. Usamos v1beta
    # 2. Especificamos el path completo del modelo
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"Genera una receta de cocina para: {query}. "
                    "Responde exclusivamente en formato JSON con esta estructura: "
                    '{"title": "Nombre", "kcal": "valor", "proteina": "valor", '
                    '"ingredients": ["item1", "item2"], "instructions": ["paso1", "paso2"], '
                    '"img_prompt": "foto profesional de {query}"}'
                )
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 1024,
            "responseMimeType": "application/json",
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            # Enviamos la petición con los headers y el config de AI Studio
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            
            # Verificación inmediata de la respuesta
            if response.status_code != 200:
                return [{"error": f"Google respondió con error {response.status_code}", "detalle": response.text}]
            
            data = response.json()
            
            # Extracción segura según la estructura v1beta
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
            return [{"error": f"Falla en la comunicación: {str(e)}"}]

@app.get("/")
async def root():
    return {"status": "online", "model": "gemini-1.5-flash-v1beta"}