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
                {"role": "system", "content": "Eres un Chef. Responde JSON con: 'title' (string), 'ingredients' (lista de strings), 'instructions' (string). Si no es comida, devuelve {'error': 'No es comida'}."},
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except:
        return {"error": "Servidor ocupado"}

@app.get("/generate-image")
def generate_image(prompt: str = Query(...)):
    url = "https://api.segmind.com/v1/flux-schnell"
    headers = {"x-api-key": os.getenv("SEGMIND_API_KEY"), "Content-Type": "application/json"}
    payload = {"prompt": f"Professional food photography of {prompt}, 8k, studio lighting", "steps": 20}
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            # LIMPIEZA QUIRÚRGICA: Quitamos cualquier carácter invisible que rompa el Base64
            img_clean = base64.b64encode(res.content).decode('utf-8').strip().replace("\n", "").replace("\r", "")
            return {"image": img_clean}
        return {"error": "API de imagen falló"}
    except:
        return {"error": "Error de conexión"}