import os, base64, requests, json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()
# Protección 1: CORS total para evitar bloqueos del navegador
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/search")
def get_recipe(query: str = Query(...)):
    try:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un Chef. Si la consulta NO es comida, responde: {'error': 'Solo recetas culinarias'}. Si ES comida, responde UN OBJETO JSON con: 'title' (string), 'ingredients' (lista), 'instructions' (string)."
                },
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"} # Protección 2: Fuerza JSON
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"error": "Error en el servidor de IA"}

@app.get("/generate-image")
def generate_image(prompt: str = Query(...)):
    url = "https://api.segmind.com/v1/flux-schnell"
    headers = {"x-api-key": os.getenv("SEGMIND_API_KEY"), "Content-Type": "application/json"}
    payload = {"prompt": f"Gourmet food photo of {prompt}, high resolution", "steps": 20}
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            # Protección 3: Limpieza absoluta del Base64
            img_b64 = base64.b64encode(res.content).decode('utf-8').strip().replace('\n', '').replace('\r', '')
            return {"image": img_b64}
        return {"error": "Error al generar imagen"}
    except:
        return {"error": "Fallo de conexión"}