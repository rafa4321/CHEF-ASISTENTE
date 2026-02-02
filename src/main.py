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

# Las API Keys deben estar configuradas como Variables de Entorno en Render
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/search")
def get_recipe(query: str = Query(...)):
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres un chef. Devuelve un OBJETO JSON con: title, ingredients (lista), instructions (string)."},
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile", # Modelo actualizado
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
        "prompt": f"Professional food photography of {prompt}, cinematic lighting, high resolution",
        "steps": 20,
        "seed": 42
    }
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            # Enviamos la imagen en base64 para que Flutter la lea con Image.memory
            return {"image": base64.b64encode(res.content).decode('utf-8')}
        return {"error": f"Segmind Error: {res.status_code}"}
    except Exception as e:
        return {"error": str(e)}