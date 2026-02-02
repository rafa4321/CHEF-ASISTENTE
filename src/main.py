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

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/search")
def get_recipe(query: str = Query(...)):
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres un chef Michelin. Devuelve un OBJETO JSON (no una lista) con title, ingredients (lista de strings) e instructions (string)."},
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        # Limpieza profunda del formato
        raw_data = json.loads(completion.choices[0].message.content)
        if isinstance(raw_data, list):
            return raw_data[0]
        return raw_data
    except Exception as e:
        return {"error": str(e)}

@app.get("/generate-image")
def generate_image(prompt: str = Query(...)):
    url = "https://api.segmind.com/v1/flux-schnell"
    headers = {"x-api-key": os.getenv("SEGMIND_API_KEY"), "Content-Type": "application/json"}
    payload = {"prompt": f"Gourmet food photo of {prompt}, professional lighting", "steps": 15}
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            return {"image": base64.b64encode(res.content).decode('utf-8')}
        return {"error": "Failed Segmind"}
    except Exception as e:
        return {"error": str(e)}