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

async def generar_imagen_ia(plato):
    """Genera imagen gourmet usando tu HF_TOKEN"""
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    prompt = f"Gourmet professional food photography of {plato}, elegant plating, 8k, highly detailed."
    try:
        async with httpx.AsyncClient() as ac:
            response = await ac.post(api_url, headers=headers, json={"inputs": prompt}, timeout=60.0)
            if response.status_code == 200:
                return f"data:image/jpeg;base64,{base64.b64encode(response.content).decode('utf-8')}"
    except: pass
    return "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"

@app.get("/search")
async def search(query: str = Query(...), personas: int = Query(2)):
    try:
        system_prompt = f"""
        Eres un Chef Pro. Responde solo en JSON y en ESPAÑOL.
        Calcula las cantidades EXACTAS para {personas} personas.
        {{"title": "NOMBRE", "kcal": "500", "prot": "30g", "ing": ["cant + item"], "ins": "pasos"}}
        """
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        data = json.loads(completion.choices[0].message.content)
        
        # Generamos la imagen real
        url_imagen = await generar_imagen_ia(data.get("title", query))

        return [{
            "title": data.get("title", query).upper(),
            "kcal": data.get("kcal", "0"),
            "proteina": data.get("prot", "0g"),
            "ingredients": data.get("ing", []),
            "instructions": data.get("ins", ""),
            "image_url": url_imagen
        }]
    except Exception as e:
        return [{"title": "ERROR", "instructions": str(e)}]