import os
import json
import httpx
import base64
import asyncio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# CORS habilitado para evitar bloqueos en Flutter Web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def generar_imagen_profesional(prompt_comida):
    # Modelo ultra-estable para evitar el error 410
    api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    token = os.getenv("HF_TOKEN")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": f"Professional food photography, {prompt_comida}, high quality, gourmet",
        "options": {"wait_for_model": True}
    }

    async with httpx.AsyncClient() as ac:
        try:
            # Sistema de 2 intentos por si el modelo está en reposo
            for _ in range(2):
                response = await ac.post(api_url, headers=headers, json=payload, timeout=35.0)
                if response.status_code == 200:
                    img_str = base64.b64encode(response.content).decode('utf-8')
                    return f"data:image/jpeg;base64,{img_str}"
                elif response.status_code == 503:
                    await asyncio.sleep(10)
                    continue
                else:
                    break
            
            # Respaldo de comida real si la IA falla (Evita el cuadro negro)
            return f"https://loremflickr.com/800/600/food,{prompt_comida.replace(' ', '')}/all"
        except:
            return f"https://ui-avatars.com/api/?name={prompt_comida}&size=512"

@app.get("/search")
async def get_recipe(query: str = Query(...)):
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Chef profesional. Devuelve SOLO JSON: {'title': str, 'ingredients': list, 'instructions': str}"},
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        receta = json.loads(completion.choices[0].message.content)
        # Generar imagen y añadirla al JSON
        receta['image_url'] = await generar_imagen_profesional(receta.get('title', query))
        return [receta]
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)