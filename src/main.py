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

async def obtener_foto_ia(prompt_plato):
    """Llamada a Hugging Face para generar la imagen real"""
    url_hf = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    try:
        async with httpx.AsyncClient() as ac:
            payload = {"inputs": f"Gourmet food photography of {prompt_plato}, professional lighting, 8k resolution"}
            response = await ac.post(url_hf, headers=headers, json=payload, timeout=40.0)
            if response.status_code == 200:
                # Convertimos el binario de la imagen a Base64 para Flutter
                img_b64 = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/jpeg;base64,{img_b64}"
    except Exception as e:
        print(f"Error en imagen: {e}")
    return "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"

@app.get("/search")
async def buscar(query: str = Query(...)):
    try:
        system_prompt = """
        Eres un ASISTENTE CULINARIO Y NUTRICIONISTA PROFESIONAL.
        REGLAS:
        1. Solo temas de cocina y salud alimentaria. Si no es culinario, rechaza.
        2. Prohibido especies protegidas (tortuga, iguana, etc.).
        3. Para condiciones médicas (diabetes, celiaquía), adapta la dieta.
        Responde estrictamente en JSON:
        {"valido": true, "error": "", "title": "...", "kcal": "...", "prot": "...", "ing": [...], "ins": [...]}
        """
        
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)

        if not res.get("valido"):
            return [{"title": "AVISO", "instructions": [res.get("error", "Consulta no permitida")], "ingredients": [], "image_url": ""}]

        # ACTIVACIÓN DE FOTO POR IA
        url_final = await obtener_foto_ia(res.get("title", query))

        return [{
            "title": res.get("title").upper(),
            "kcal": res.get("kcal"),
            "proteina": res.get("prot"),
            "ingredients": res.get("ing"),
            "instructions": res.get("ins"), # Enviado como lista de pasos
            "image_url": url_final
        }]
    except Exception as e:
        return [{"title": "ERROR", "instructions": [str(e)]}]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))