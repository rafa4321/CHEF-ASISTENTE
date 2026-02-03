import os, base64, requests, json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()
# Permitimos comunicación total entre el navegador y el servidor
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/search")
def get_recipe(query: str = Query(...)):
    try:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un Chef Profesional. Responde ÚNICAMENTE con un objeto JSON (sin corchetes al inicio). Estructura: {'title': str, 'ingredients': list, 'instructions': str}. Si no es comida, devuelve {'error': 'Solo cocino alimentos'}."
                },
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        # Verificación de integridad
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Error en receta: {e}")
        return {"error": "No se pudo obtener la receta"}

@app.get("/generate-image")
def generate_image(prompt: str = Query(...)):
    url = "https://api.segmind.com/v1/flux-schnell"
    headers = {"x-api-key": os.getenv("SEGMIND_API_KEY"), "Content-Type": "application/json"}
    payload = {"prompt": f"Professional gourmet food photography of {prompt}, 8k, realistic", "steps": 20}
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            # LIMPIEZA QUIRÚRGICA: Eliminamos saltos de línea y espacios para evitar el error de visualización
            img_b64 = base64.b64encode(res.content).decode('utf-8').strip().replace('\n', '').replace('\r', '')
            return {"image": img_b64}
        return {"error": "Fallo en la generación de imagen"}
    except Exception as e:
        print(f"Error en imagen: {e}")
        return {"error": "Error de conexión con Segmind"}