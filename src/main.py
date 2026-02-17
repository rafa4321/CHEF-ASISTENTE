import os
import json
import httpx
import base64
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Configuración de CORS para que tu App de Flutter pueda conectarse
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def generar_foto_ia(nombre_plato):
    # Usamos la nueva URL de Hugging Face (Router)
    url_hf = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    
    # Prompt técnico para asegurar que la imagen coincida con el plato
    prompt_detallado = f"A gourmet professional food photo of {nombre_plato}, Venezuelan cuisine style, high quality, 4k, cinematic lighting, appetizing"
    
    try:
        async with httpx.AsyncClient() as ac:
            payload = {"inputs": prompt_detallado}
            # Timeout largo (60s) porque generar una imagen desde cero toma tiempo
            response = await ac.post(url_hf, headers=headers, json=payload, timeout=60.0)
            
            if response.status_code == 200:
                img_b64 = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/jpeg;base64,{img_b64}"
            else:
                print(f"Error en HF: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Excepción en imagen: {e}")
    
    # Imagen de respaldo si la IA falla
    return "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"

@app.get("/search")
async def buscar(query: str = Query(...)):
    try:
        system_prompt = """
        Eres un Chef Profesional. Responde exclusivamente en formato JSON.
        El JSON debe tener esta estructura:
        {"title": "NOMBRE", "kcal": "número", "prot": "número", "ing": ["lista"], "ins": ["pasos"]}
        """
        
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)
        
        # Generamos la imagen basada en el título que dio la IA
        foto_base64 = await generar_foto_ia(res.get("title", query))

        return [{
            "title": res.get("title", "RECETA").upper(),
            "kcal": f"{res.get('kcal', '---')} Kcal",
            "proteina": f"{res.get('prot', '---')} Prot",
            "ingredients": res.get("ing", []),
            "instructions": res.get("ins", []),
            "image_url": foto_base64
        }]
    except Exception as e:
        print(f"Error General: {e}")
        return [{"title": "ERROR", "instructions": [str(e)], "image_url": ""}]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))