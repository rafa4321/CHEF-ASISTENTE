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
    """Petición a Hugging Face para generar la imagen real"""
    url_hf = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    try:
        async with httpx.AsyncClient() as ac:
            payload = {
                "inputs": f"Professional gourmet food photography of {nombre_plato}, 8k, appetizing, top view",
            }
            response = await ac.post(url_hf, headers=headers, json=payload, timeout=40.0)
            if response.status_code == 200:
                img_b64 = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/jpeg;base64,{img_b64}"
    except:
        pass
    return "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"

@app.get("/search")
async def buscar(query: str = Query(...)):
    try:
        system_prompt = """
        Eres un ASISTENTE EXPERTO EN ARTES CULINARIAS.
        - Solo cocina y nutrición. 
        - Si la consulta NO es culinaria (ej. 'retrovisor'), responde: {"es_valido": false, "motivo": "No soy experto en ese tema, solo cocina."}
        - Prohibido especies protegidas.
        Responde en JSON: {"es_valido": true, "motivo": "", "title": "...", "kcal": "...", "prot": "...", "ing": [...], "ins": [...]}
        """
        
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)

        if not res.get("es_valido", True):
            return [{"title": "AVISO", "instructions": [res.get("motivo")], "ingredients": [], "image_url": ""}]

        foto = await generar_foto_ia(res.get("title", query))

        return [{
            "title": res.get("title", query).upper(),
            "kcal": res.get("kcal", "---"),
            "proteina": res.get("prot", "---"),
            "ingredients": res.get("ing", []),
            "instructions": res.get("ins", []),
            "image_url": foto
        }]
    except Exception as e:
        return [{"title": "ERROR", "instructions": [str(e)]}]