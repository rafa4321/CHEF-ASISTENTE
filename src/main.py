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
        1. Solo cocina y nutrición. Si piden algo no relacionado (ej. mecánica, electrónica), responde amablemente que no es tu área.
        2. PROHIBIDO recetas con especies protegidas (tortugas, iguanas, ballenas, etc.). Responde que es ilegal y poco ético.
        3. DIETAS ESPECIALES: Si piden para celiacos, diabéticos o hipertensos, adapta la receta estrictamente.
        
        FORMATO DE RESPUESTA (JSON):
        {
          "es_cocina": true/false,
          "mensaje_error": "Solo si no es cocina o es especie protegida",
          "title": "Nombre",
          "kcal": "valor",
          "prot": "valor",
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

        # Validación de Identidad y Ética
        if not res.get("es_cocina", True) or res.get("mensaje_error"):
            return [{
                "title": "AVISO DEL CHEF",
                "instructions": [res.get("mensaje_error", "No puedo ayudarte con esa solicitud.")],
                "ingredients": [],
                "image_url": "https://images.unsplash.com/photo-1594312915251-48db9280c8f1?w=500" # Foto de aviso
            }]

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))