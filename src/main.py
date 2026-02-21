import os
import json
import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuración de CORS para que Flutter pueda conectarse desde el celular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
async def buscar_receta(query: str = Query(...)):
    api_key = os.getenv("GOOGLE_API_KEY")
    # Usamos la versión v1 de producción para evitar el error 404 de la v1beta
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"Genera una receta de cocina para: {query}. "
                    "Responde exclusivamente en formato JSON con esta estructura: "
                    '{"title": "Nombre", "kcal": "valor", "proteina": "valor", '
                    '"ingredients": ["item1", "item2"], "instructions": ["paso1", "paso2"], '
                    '"img_prompt": "foto gourmet de {query}"}'
                )
            }]
        }]
    }

    async with httpx.AsyncClient() as client:
        try:
            # Enviamos la petición a Google
            response = await client.post(url, json=payload, timeout=30.0)
            data = response.json()
            
            # Verificamos si Google devolvió un error de cuota o llave
            if "error" in data:
                return [{"error": f"Google API Error: {data['error']['message']}"}]

            # Extraemos el texto de la respuesta
            texto_ia = data['candidates'][0]['content']['parts'][0]['text']
            
            # Limpiamos el texto por si la IA devuelve bloques de código markdown
            texto_ia = texto_ia.replace("```json", "").replace("```", "").strip()
            
            # Convertimos el texto en un objeto JSON de Python
            receta = json.loads(texto_ia)
            
            # Generamos la URL de la imagen usando Pollinations (Gratis y rápido)
            img_url = f"https://image.pollinations.ai/prompt/{receta.get('img_prompt', query).replace(' ', '%20')}?model=flux&width=1024&height=1024&nologo=true"

            return [{
                "title": receta.get('title', query).upper(),
                "kcal": f"{receta.get('kcal', '0')} Kcal",
                "proteina": f"{receta.get('proteina', '0')} Prot",
                "ingredients": receta.get('ingredients', []),
                "instructions": receta.get('instructions', []),
                "image_url": img_url
            }]
        except Exception as e:
            return [{"error": f"Error crítico: {str(e)}"}]

@app.get("/")
async def root():
    return {"status": "online", "message": "Chef Asistente API v1.0"}