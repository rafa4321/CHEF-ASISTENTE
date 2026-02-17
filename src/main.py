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
    # MODELO FLUX (Más rápido y mejor calidad)
    url_hf = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    
    try:
        async with httpx.AsyncClient() as ac:
            payload = {
                "inputs": f"Professional gourmet food photography of {nombre_plato}, photorealistic, 4k, delicious, top view",
            }
            # El modelo FLUX es rápido, 30s de timeout es suficiente
            response = await ac.post(url_hf, headers=headers, json=payload, timeout=30.0)
            
            if response.status_code == 200:
                img_b64 = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/jpeg;base64,{img_b64}"
            else:
                print(f"Error en HF ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"Excepción en IA de imagen: {e}")
    
    # Si falla la IA por cuota, devolvemos esta de respaldo
    return "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"

@app.get("/search")
async def buscar(query: str = Query(...)):
    try:
        system_prompt = """
        Eres un Chef experto. Responde SIEMPRE en JSON estricto.
        Si la consulta NO es cocina, responde: {"valido": false, "error": "Solo cocina."}
        Si ES cocina, responde:
        {"valido": true, "title": "Nombre", "kcal": "valor", "prot": "valor", "ing": ["lista"], "ins": ["pasos"]}
        """
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        res = json.loads(completion.choices[0].message.content)

        if not res.get("valido", True):
            return [{"title": "AVISO", "instructions": [res.get("error")], "image_url": ""}]

        # Llamada a la nueva IA de imagen
        foto_base64 = await generar_foto_ia(res.get("title", query))

        return [{
            "title": res.get("title", "").upper(),
            "kcal": f"{res.get('kcal')} Kcal",
            "proteina": f"{res.get('prot')} Prot",
            "ingredients": res.get("ing", []),
            "instructions": res.get("ins", []),
            "image_url": foto_base64
        }]
    except Exception as e:
        return [{"title": "ERROR", "instructions": [str(e)]}]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))