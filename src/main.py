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
                {"role": "system", "content": "Eres un Chef Gourmet. Si el usuario pide algo que NO sea comida, responde: {'error': 'Lo siento, solo cocino comida real.'}. Si es comida, devuelve JSON con: title, ingredients (lista), instructions."},
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
    payload = {"prompt": f"Professional food photography of {prompt}, cinematic lighting, 8k", "steps": 20}
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            # LIMPIEZA MILITAR: Eliminamos cualquier carácter extraño del Base64
            img_str = base64.b64encode(res.content).decode('utf-8').replace('\n', '').replace('\r', '')
            return {"image": img_str}
        return {"error": "API Error"}
    except Exception as e:
        return {"error": str(e)}