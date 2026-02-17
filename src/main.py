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
    """Genera imagen real usando Hugging Face (SDXL)"""
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    try:
        async with httpx.AsyncClient() as ac:
            # Prompt optimizado para comida gourmet
            payload = {"inputs": f"Professional food photography of {descripcion}, gourmet plating, 8k, highly detailed"}
            response = await ac.post(api_url, headers=headers, json=payload, timeout=40.0)
            if response.status_code == 200:
                return f"data:image/jpeg;base64,{base64.b64encode(response.content).decode('utf-8')}"
    except: pass
    # Imagen de respaldo si falla la IA
    return "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1000"

@app.get("/search")
async def buscar(query: str = Query(...)):
    try:
        system_prompt = """
        Eres un Chef Profesional. Responde ESTRICTAMENTE en JSON con esta estructura:
        {
          "title": "Nombre",
          "kcal": "500",
          "prot": "25g",
          "ing": ["item 1", "item 2"],
          "ins": ["Paso 1 detallado", "Paso 2 detallado"]
        }
        """
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        data = json.loads(completion.choices[0].message.content)
        foto = await generar_imagen_ia(data.get("title", query))

        return [{
            "title": data.get("title", query).upper(),
            "kcal": data.get("kcal", "---"),
            "proteina": data.get("prot", "---"),
            "ingredients": data.get("ing", []),
            "instructions": data.get("ins", []), # Lista para Flutter
            "image_url": foto
        }]
    except Exception as e:
        return [{"title": "ERROR", "instructions": [str(e)], "ingredients": []}]