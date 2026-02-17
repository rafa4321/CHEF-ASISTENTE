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

async def generar_foto_ia(nombre_plato):
    """Genera una imagen única para el plato usando Hugging Face"""
    url_hf = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    try:
        async with httpx.AsyncClient() as ac:
            # Prompt ultra-detallado para evitar imágenes genéricas
            payload = {
                "inputs": f"High quality gourmet photo of {nombre_plato}, realistic, 8k, detailed texture, professional plating, blurred background",
                "parameters": {"wait_for_model": True} 
            }
            response = await ac.post(url_hf, headers=headers, json=payload, timeout=60.0)
            if response.status_code == 200:
                img_b64 = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/jpeg;base64,{img_b64}"
    except Exception as e:
        print(f"Error HF: {e}")
    return "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"

@app.get("/search")
async def buscar(query: str = Query(...)):
    try:
        # Prompt del sistema reforzado para máxima precisión técnica
        system_prompt = """
        Eres un Master Chef con 3 estrellas Michelin. Tu precisión en medidas y técnicas es absoluta.
        Reglas:
        1. Si la consulta no es comida (ej. 'retrovisor'), responde {"valido": false, "motivo": "Solo gastronomía."}.
        2. No uses especies protegidas.
        3. Formato JSON estricto: 
        {"valido": true, "title": "Nombre Exacto", "kcal": "número exacto", "prot": "gramos", "ing": ["lista detallada"], "ins": ["pasos técnicos paso a paso"]}
        """
        
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile", # Modelo de alta precisión
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)

        if not res.get("valido", True):
            return [{"title": "AVISO", "instructions": [res.get("motivo", "Error")], "image_url": ""}]

        # Generar la imagen específica para ESTE título de receta
        foto_resultado = await generar_foto_ia(res.get("title", query))

        return [{
            "title": res.get("title").upper(),
            "kcal": f"{res.get('kcal')} Kcal",
            "proteina": f"{res.get('prot')}g Proteína",
            "ingredients": res.get("ing"),
            "instructions": res.get("ins"),
            "image_url": foto_resultado # Aquí va la imagen generada
        }]
    except Exception as e:
        return [{"title": "ERROR", "instructions": [str(e)]}]