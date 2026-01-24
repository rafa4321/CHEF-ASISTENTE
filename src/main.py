from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import requests
from dotenv import load_dotenv

# Cargamos las variables
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

@app.get("/")
async def root():
    return {"message": "Chef Asistente API is Online", "status": "ok"}

@app.get("/search")
async def search(query: str):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="Falta API Key de Groq.")

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Eres un Chef experto. Tu respuesta debe ser exclusivamente un objeto JSON válido."},
            {"role": "user", "content": f"Genera una receta para: {query}"}
        ],
        "response_format": {"type": "json_object"}
    }

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
        content = response.json()['choices'][0]['message']['content']
        return [json.loads(content)]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))