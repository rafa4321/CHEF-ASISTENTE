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
    
    # LA FÓRMULA GANADORA: Usamos la v1 estable para evitar el 404 de la v1beta
    # Y usamos el nombre del modelo sin el prefijo 'models/' que a veces causa conflicto
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"Genera una receta para: {query}. "
                    "Responde estrictamente con un JSON: "
                    '{"title": "Nombre", "kcal": "valor", "proteina": "valor", '
                    '"ingredients": ["lista"], "instructions": ["pasos"], '
                    '"img_prompt": "foto de {query}"}'
                )
            }]
        }]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            data = response.json()
            
            # Si la v1 falla, el código nos dirá exactamente por qué
            if "error" in data:
                return [{"error": f"Google dice: {data['error']['message']}"}]

            texto_ia = data['candidates'][0]['content']['parts'][0]['text']
            # Limpiamos basura de markdown
            texto_ia = texto_ia.replace("```json", "").replace("```", "").strip()
            
            receta = json.loads(texto_ia)
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
            return [{"error": f"Error técnico: {str(e)}"}]

@app.get("/")
async def root():
    return {"status": "online", "message": "Chef API Sincronizada"}