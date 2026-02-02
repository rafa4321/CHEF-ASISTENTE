import os
import base64
import requests
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# SEGURIDAD: Render leerá estas llaves desde su panel de control
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SEGMIND_API_KEY = os.getenv("SEGMIND_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

@app.get("/")
def home():
    return {"status": "Servidor Seguro Activo"}

@app.get("/search")
def get_recipe(query: str = Query(...)):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres un chef Michelin. Devuelve JSON: {'title': '', 'ingredients': [], 'instructions': ''}"},
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        return json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/generate-image")
def generate_image(prompt: str = Query(...)):
    url = "https://api.segmind.com/v1/flux-schnell"
    payload = {"prompt": f"Gourmet photo of {prompt}, 8k", "steps": 20}
    headers = {"x-api-key": SEGMIND_API_KEY, "Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return {"image": base64.b64encode(response.content).decode('utf-8')}
        return {"error": "Fallo en imagen"}, 500
    except Exception as e:
        return {"error": str(e)}, 500