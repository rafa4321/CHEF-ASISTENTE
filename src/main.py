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
    """Comunicación con Hugging Face para generar la fotografía real"""
    url_hf = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    try:
        async with httpx.AsyncClient() as ac:
            payload = {
                "inputs": f"Professional gourmet food photography of {nombre_plato}, high resolution, 8k, appetizing, cinematic lighting",
            }
            response = await ac.post(url_hf, headers=headers, json=payload, timeout=45.0)
            if response.status_code == 200:
                # Convertimos el binario de la imagen a Base64 para enviarlo a la App
                img_b64 = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/jpeg;base64,{img_b64}"
    except Exception as e:
        print(f"Error en IA de imagen: {e}")
    # Imagen de respaldo si la IA falla
    return "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"

@app.get("/search")
async def buscar(query: str = Query(...)):
    try:
        system_prompt = """
        Eres un ASISTENTE EXPERTO EN ARTES CULINARIAS Y NUTRICIÓN.
        
        REGLAS:
        1. IDENTIDAD: Solo cocina. Si piden temas ajenos (ej. 'retrovisor'), responde: {"valido": false, "error": "Solo puedo ayudarte con temas culinarios y nutrición."}
        2. ÉTICA: Prohibido cocinar especies protegidas. Responde: {"valido": false, "error": "No proceso recetas de especies protegidas por razones éticas y legales."}
        3. SALUD: Adapta menús para diabéticos, celiacos o hipertensos si se solicita.
        
        FORMATO JSON OBLIGATORIO:
        {"valido": true, "error": "", "title": "Nombre", "kcal": "valor", "prot": "valor", "ing": ["lista"], "ins": ["pasos"]}
        """
        
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)

        if not res.get("valido", True):
            return [{
                "title": "AVISO CULINARIO",
                "instructions": [res.get("error")],
                "ingredients": [],
                "image_url": "https://images.unsplash.com/photo-1594312915251-48db9280c8f1?w=500"
            }]

        # Generar la fotografía con IA
        foto_base64 = await generar_foto_ia(res.get("title", query))

        return [{
            "title": res.get("title", query).upper(),
            "kcal": res.get("kcal", "---"),
            "proteina": res.get("prot", "---"),
            "ingredients": res.get("ing", []),
            "instructions": res.get("ins", []),
            "image_url": foto_base64
        }]
    except Exception as e:
        return [{"title": "ERROR", "instructions": [str(e)], "ingredients": []}]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))