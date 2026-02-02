import os
import base64
import requests
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Configuración de CORS obligatoria para Flutter Web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente de Groq con el modelo actualizado
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/")
def home():
    return {"status": "Servidor Chef IA Online"}

@app.get("/search")
def get_recipe(query: str = Query(...)):
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres un chef Michelin. Devuelve un JSON con: title, ingredients (lista de strings) e instructions (string). Responde en español."},
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

@app.get("/generate-image")
def generate_image(prompt: str = Query(...)):
    url = "https://api.segmind.com/v1/flux-schnell"
    headers = {"x-api-key": os.getenv("SEGMIND_API_KEY"), "Content-Type": "application/json"}
    payload = {
        "prompt": f"Professional gourmet food photography of {prompt}, 8k, elegant plating",
        "steps": 20
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            # Convertir imagen a Base64
            img_b64 = base64.b64encode(response.content).decode('utf-8')
            return {"image": img_b64}
        return {"error": "Error en Segmind", "code": response.status_code}
    except Exception as e:
        return {"error": str(e)}