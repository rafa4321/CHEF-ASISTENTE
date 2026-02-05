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
                {
                    "role": "system", 
                    "content": "Eres un Chef. Responde ÚNICAMENTE con un JSON: {'title': str, 'ingredients': list, 'instructions': str}."
                },
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"error": f"Error en Groq: {str(e)}"}

@app.get("/generate-image")
def generate_image(prompt: str = Query(...)):
    try:
        # CONTRATO NUEVO: Usamos Pollinations.ai (Gratis y sin API Key)
        # Limpiamos el prompt para que sea una URL válida
        clean_prompt = prompt.replace(" ", "%20")
        url = f"https://pollinations.ai/p/{clean_prompt}?width=1024&height=1024&seed=42&model=flux"
        
        res = requests.get(url, timeout=20)
        
        if res.status_code == 200:
            # Convertimos la imagen binaria a Base64 para Flutter
            img_b64 = base64.b64encode(res.content).decode('utf-8')
            return {"image": img_b64}
        else:
            return {"error": f"Error de imagen: Status {res.status_code}"}
    except Exception as e:
        return {"error": f"Excepción en imagen: {str(e)}"}