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
    """Se comunica con Hugging Face para generar la imagen real del plato"""
    url_hf = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    try:
        async with httpx.AsyncClient() as ac:
            # Prompt optimizado para realismo gourmet
            payload = {
                "inputs": f"Professional gourmet food photography of {nombre_plato}, high resolution, 8k, cinematic lighting, appetizing, top view",
                "parameters": {"negative_prompt": "blurry, low quality, distorted food"}
            }
            response = await ac.post(url_hf, headers=headers, json=payload, timeout=40.0)
            if response.status_code == 200:
                # Convertimos el binario recibido en Base64 para enviarlo a Flutter
                img_b64 = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/jpeg;base64,{img_b64}"
    except Exception as e:
        print(f"Error generando imagen: {e}")
    # Imagen de respaldo si falla la comunicación con la IA
    return "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"

@app.get("/search")
async def buscar(query: str = Query(...)):
    try:
        system_prompt = """
        Eres un ASISTENTE EXPERTO EN ARTES CULINARIAS Y NUTRICIÓN.
        
        REGLAS ESTRICTAS DE RESPUESTA:
        1. IDENTIDAD: Solo cocina y nutrición. Si piden algo no culinario (ej. 'retrovisor'), responde: {"es_valido": false, "motivo": "Lo siento, como asistente culinario no puedo procesar temas ajenos a la gastronomía."}
        2. ÉTICA AMBIENTAL: Prohibido cocinar especies protegidas (tortugas, iguanas, etc.). Responde: {"es_valido": false, "motivo": "Esa solicitud incluye especies protegidas y no es ético ni legal procesarla."}
        3. SALUD: Crea dietas específicas para celiacos, diabéticos, hipertensos, veganos, etc., adaptando ingredientes (ej. sin sal, sin azúcar).
        
        FORMATO JSON:
        {"es_valido": true, "motivo": "", "title": "Nombre", "kcal": "valor", "prot": "valor", "ing": ["..."], "ins": ["..."]}
        """
        
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)

        if not res.get("es_valido", True):
            return [{
                "title": "AVISO DEL CHEF",
                "instructions": [res.get("motivo")],
                "ingredients": [],
                "image_url": "https://images.unsplash.com/photo-1594312915251-48db9280c8f1?w=500"
            }]

        # Generar fotografía mediante IA
        foto_final = await generar_foto_ia(res.get("title", query))

        return [{
            "title": res.get("title", query).upper(),
            "kcal": res.get("kcal", "---"),
            "proteina": res.get("prot", "---"),
            "ingredients": res.get("ing", []),
            "instructions": res.get("ins", []),
            "image_url": foto_final
        }]
    except Exception as e:
        return [{"title": "ERROR", "instructions": [str(e)]}]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))