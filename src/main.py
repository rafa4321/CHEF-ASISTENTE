import os, base64, requests, json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/search")
def get_recipe(query: str = Query(...)):
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres un Chef. Responde ÚNICAMENTE un JSON con: 'title', 'ingredients' (lista de strings) e 'instructions' (string). Si no es comida, devuelve {'error': 'No es comida'}"},
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        # Forzamos que la respuesta sea un objeto plano, nunca una lista
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"error": "Error de servidor"}

@app.get("/generate-image")
def generate_image(prompt: str = Query(...)):
    url = "https://api.segmind.com/v1/flux-schnell"
    headers = {"x-api-key": os.getenv("SEGMIND_API_KEY"), "Content-Type": "application/json"}
    payload = {"prompt": f"Gourmet food photo of {prompt}", "steps": 20}
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            # Limpieza total del Base64 para evitar el error de subtipo
            img_clean = base64.b64encode(res.content).decode('utf-8').strip()
            return {"image": img_clean}
        return {"error": "API Error"}
    except:
        return {"error": "Connection error"}