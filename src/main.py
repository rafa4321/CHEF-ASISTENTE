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

# Canal Profesional: Stable Diffusion vía Hugging Face
async def generar_imagen_michelin(prompt_comida):
    # Necesitarás esta Key en Render: HF_TOKEN
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    
    payload = {
        "inputs": f"Gourmet professional food photography of {prompt_comida}, 8k, michelin star plating, studio lighting, appetizing textures",
    }
    
    async with httpx.AsyncClient() as ac:
        try:
            response = await ac.post(api_url, headers=headers, json=payload, timeout=60.0)
            if response.status_code == 200:
                # Convertimos la imagen a Base64 para saltar el error 403/406 definitivamente
                encoded_img = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/jpeg;base64,{encoded_img}"
            return None
        except:
            return None

@app.get("/search")
async def get_recipe(query: str = Query(...)):
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Chef Gourmet. Responde SOLO JSON: {'title': str, 'ingredients': list, 'instructions': str}."},
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        receta = json.loads(completion.choices[0].message.content)
        
        # Generar la imagen y enviarla como datos seguros
        receta['image_url'] = await generar_imagen_michelin(receta.get('title', query))
        return [receta]
    except Exception as e:
        return {"error": str(e)}