import os
import base64
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Esto es vital para que Flutter no se bloquee
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Ruta de prueba raíz (Para verificar si el servidor responde)
@app.get("/")
def read_root():
    return {"status": "Servidor Chef Asistente Activo"}

# 2. Ruta de búsqueda (La que Flutter necesita)
@app.get("/search")
def search(query: str = Query(...)):
    return {
        "title": f"Deliciosa Receta de {query}",
        "ingredients": ["Ingrediente de prueba 1", "Ingrediente de prueba 2"],
        "instructions": "Mezclar todo y disfrutar."
    }

# 3. Ruta para la imagen (Provisional para pruebas)
@app.get("/generate-image")
def generate_image(prompt: str = Query(...)):
    return {"image": "base64_provisional_aqui"}


SEGMIND_API_KEY = "SG_c687338eb444bfb6" # Reemplaza con tu llave real

@app.get("/generate-image")
def generate_image(prompt: str = Query(...)):
    url = "https://api.segmind.com/v1/flux-schnell"
    payload = {
        "prompt": f"Professional food photography of {prompt}, gourmet style, 8k",
        "steps": 20,
        "seed": 12345
    }
    headers = {
        "x-api-key": SEGMIND_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        # Timeout de 30 segundos para evitar que la app se quede cargando infinito
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            encoded = base64.b64encode(response.content).decode('utf-8')
            return {"image": encoded}
        return {"error": "Fallo en IA"}, response.status_code
    except Exception as e:
        return {"error": str(e)}, 500