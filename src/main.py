import os
import json
import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuración de CORS para que tu App de Flutter pueda conectarse sin problemas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
async def buscar_receta(query: str = Query(...)):
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # Motor de máxima potencia: Gemini 2.0 Flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"Genera una receta deliciosa para: {query}. "
                    "Responde estrictamente en formato JSON con esta estructura: "
                    '{"title": "Nombre", "kcal": "valor", "proteina": "valor", '
                    '"ingredients": ["ingrediente 1", "ingrediente 2"], '
                    '"instructions": ["paso 1", "paso 2"], '
                    '"img_prompt": "comida gourmet de {query}"}'
                )
            }]
        }]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=30.0)
            data = response.json()
            
            # Si hay algún error, lo capturamos
            if "error" in data:
                return [{"error": f"Error de API: {data['error']['message']}"}]

            texto_ia = data['candidates'][0]['content']['parts'][0]['text']
            # Limpiamos el JSON por si la IA agrega etiquetas markdown
            texto_ia = texto_ia.replace("```json", "").replace("```", "").strip()
            
            receta = json.loads(texto_ia)
            
            # Generador de imagen Flux para que la receta se vea increíble
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
            return [{"error": f"Error en el servidor: {str(e)}"}]

@app.get("/")
async def root():
    return {"status": "online", "mode": "Premium (Gemini 2.0 Flash)"}