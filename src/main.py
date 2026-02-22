import os
import json
import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/search")
async def buscar_receta(query: str = Query(...)):
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # USAMOS TU MODELO ACTUAL: gemini-2.0-flash (visto en tu captura)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"Genera una receta para: {query}. "
                    "Responde SOLO con un objeto JSON con esta estructura: "
                    '{"title": "Nombre", "kcal": "valor", "proteina": "valor", '
                    '"ingredients": ["item1"], "instructions": ["paso1"], '
                    '"img_prompt": "foto de {query}"}'
                )
            }]
        }]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=30.0)
            data = response.json()
            
            if "error" in data:
                return [{"error": f"Google dice: {data['error']['message']}"}]

            texto_ia = data['candidates'][0]['content']['parts'][0]['text']
            # Limpiamos el texto de posibles etiquetas de markdown
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
            return [{"error": f"Fallo en el servidor: {str(e)}"}]

@app.get("/")
async def root():
    return {"status": "online", "model": "Gemini 2.0 Flash Sincronizado"}