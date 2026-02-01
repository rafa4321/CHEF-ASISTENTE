import os
import base64
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuración de CORS: Vital para que Flutter Web no de error
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# REEMPLAZA CON TU LLAVE DE SEGMIND
SEGMIND_API_KEY = "SG_c687338eb444bfb6" 

@app.get("/")
def home():
    return {"status": "Chef Asistente API Corriendo"}

@app.get("/generate-image")
def generate_image(prompt: str = Query(...)):
    url = "https://api.segmind.com/v1/flux-schnell"
    
    # Prompt técnico para evitar waffles y asegurar fotos gourmet
    payload = {
        "prompt": f"Professional gourmet food photography of {prompt}, 8k, studio lighting, elegant plating",
        "steps": 20,
        "seed": 12345
    }
    headers = {
        "x-api-key": SEGMIND_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            # Convertimos la imagen binaria a Base64
            encoded_image = base64.b64encode(response.content).decode('utf-8')
            return {"image_base64": encoded_image}
        return {"error": "Error en Segmind", "details": response.text}, response.status_code
    except Exception as e:
        return {"error": str(e)}, 500