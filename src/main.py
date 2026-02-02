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

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SEGMIND_API_KEY = os.getenv("SEGMIND_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

@app.get("/search")
def get_recipe(query: str = Query(...)):
    try:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un chef Michelin. Devuelve un JSON con esta estructura: {'title': '...', 'ingredients': [], 'instructions': '...'}. IMPORTANTE: No devuelvas una lista [], devuelve solo el objeto {}."
                },
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        # Validación extra de seguridad
        data = json.loads(completion.choices[0].message.content)
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        return data
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/generate-image")
def generate_image(prompt: str = Query(...)):
    url = "https://api.segmind.com/v1/flux-schnell"
    headers = {"x-api-key": SEGMIND_API_KEY, "Content-Type": "application/json"}
    payload = {"prompt": f"Gourmet plating of {prompt}, high resolution, food photography", "steps": 20}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return {"image": base64.b64encode(response.content).decode('utf-8')}
        return {"error": "Error en Segmind"}, 500
    except Exception as e:
        return {"error": str(e)}, 500