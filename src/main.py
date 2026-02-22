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
    # Cambiamos a 'gemini-1.5-flash-latest' que es el alias universal
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": f"Receta para {query} en JSON simple: titulo, kcal, proteina, ingredientes (lista), instrucciones (lista)."}]
        }]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            res_data = response.json()
            
            if response.status_code != 200:
                return [{"error": "Google rechazó la petición", "status": response.status_code, "data": res_data}]

            texto = res_data['candidates'][0]['content']['parts'][0]['text']
            # Limpieza manual de markdown
            if "```json" in texto:
                texto = texto.split("```json")[1].split("```")[0]
            
            receta = json.loads(texto)
            return [{
                "title": receta.get("titulo", query).upper(),
                "kcal": receta.get("kcal", "N/A"),
                "proteina": receta.get("proteina", "N/A"),
                "ingredients": receta.get("ingredientes", []),
                "instructions": receta.get("instrucciones", []),
                "image_url": f"[https://image.pollinations.ai/prompt/](https://image.pollinations.ai/prompt/){query.replace(' ', '%20')}?model=flux"
            }]
        except Exception as e:
            return [{"error": str(e)}]

@app.get("/")
async def root():
    return {"status": "online", "ayuda": "Usa /search?query=pizza (asegurate de usar '?' y no '%3F')"}