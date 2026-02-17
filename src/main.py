import os
import json
import httpx
import base64
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def generar_imagen_ia(descripcion):
    """Genera imagen gourmet usando Hugging Face"""
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    try:
        async with httpx.AsyncClient() as ac:
            prompt = f"Gourmet professional food photography of {descripcion}, 8k, highly detailed, cinematic lighting"
            response = await ac.post(api_url, headers=headers, json={"inputs": prompt}, timeout=40.0)
            if response.status_code == 200:
                return f"data:image/jpeg;base64,{base64.b64encode(response.content).decode('utf-8')}"
    except: pass
    return "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1000"

@app.get("/search")
async def buscar(query: str = Query(...)):
    try:
        system_prompt = """
        Eres un ASISTENTE EXPERTO EN ARTES CULINARIAS Y NUTRICIÓN.
        
        REGLAS DE SEGURIDAD Y ÉTICA:
        1. Solo cocina y nutrición. Si piden algo ajeno (ej. 'retrovisor'), responde que no es tu área.
        2. PROHIBIDO recetas con especies protegidas (tortugas, iguanas, etc.). Responde que es ilegal.
        3. SALUD: Si piden dietas para celiacos, diabéticos, hipertensos, etc., adapta el menú estrictamente.
        
        FORMATO JSON:
        {
          "es_valido": true/false,
          "error_msg": "Mensaje de rechazo si aplica",
          "title": "Nombre",
          "kcal": "Ej: 500 Kcal (Variable según ración)",
          "prot": "Ej: 25g Prot",
          "ing": ["lista"],
          "ins": ["paso 1", "paso 2"]
        }
        """
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)

        if not res.get("es_valido", True):
            return [{"title": "AVISO", "instructions": [res.get("error_msg", "Consulta no culinaria")], "ingredients": []}]

        foto = await generar_imagen_ia(res.get("title", query))

        return [{
            "title": res.get("title", query).upper(),
            "kcal": res.get("kcal", "---"),
            "proteina": res.get("prot", "---"),
            "ingredients": res.get("ing", []),
            "instructions": res.get("ins", []),
            "image_url": foto
        }]
    except Exception as e:
        return [{"title": "ERROR", "instructions": [str(e)], "ingredients": []}]