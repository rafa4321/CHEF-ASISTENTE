import os
import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/search")
async def buscar_receta(query: str = Query(...)):
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # Probamos con el modelo más básico y universal para asegurar conexión
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": f"Receta corta de {query} en JSON"}]}]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=30.0)
            res_data = response.json()
            
            # Si sigue dando 404, pediremos la lista de modelos disponibles
            if response.status_code == 404:
                list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                list_res = await client.get(list_url)
                return {
                    "error": "El modelo no fue encontrado",
                    "tus_modelos_disponibles": list_res.json()
                }
            
            return res_data
        except Exception as e:
            return {"error_tecnico": str(e)}

@app.get("/")
async def root():
    return {"status": "Proyecto Limpio Listo"}