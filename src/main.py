import os
import base64
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Abre el paso a Flutter Web para evitar bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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