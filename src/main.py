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
                {"role": "system", "content": "Responde SIEMPRE en formato JSON puro (sin listas [] afuera). Estructura: {'title': str, 'ingredients': list, 'instructions': str}. Si no es comida, responde: {'error': 'No es comida'}"},
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        # Aseguramos que devolvemos el objeto directamente
        return json.loads(completion.choices[0].message.content)
    except Exception:
        return {"error": "Error al generar receta"}

@app.get("/generate-image")
def generate_image(prompt: str = Query(...)):
    url = "https://api.segmind.com/v1/flux-schnell"
    headers = {"x-api-key": os.getenv("SEGMIND_API_KEY"), "Content-Type": "application/json"}
    payload = {"prompt": f"Gourmet food photo of {prompt}, professional lighting, 8k", "steps": 20}
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            # Limpieza crítica para evitar que la imagen se rompa en el navegador
            img_b64 = base64.b64encode(res.content).decode('utf-8').strip().replace('\n', '')
            return {"image": img_b64}
        return {"error": "API Error"}
    except Exception:
        return {"error": "Connection Error"}