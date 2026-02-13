import os
import json
import httpx
import base64
import asyncio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Configuración de CORS para que tu App de Flutter pueda comunicarse sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def generar_imagen_profesional(prompt_comida):
    """
    Genera una imagen usando Hugging Face y la convierte a Base64.
    Esto evita errores 403 (Forbidden) y 406.
    """
    # Usamos el modelo Stable Diffusion XL para calidad fotográfica
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    token = os.getenv("HF_TOKEN")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": f"Gourmet food photography, professional plating of {prompt_comida}, michelin star style, 8k resolution, highly detailed, studio lighting",
        "options": {"wait_for_model": True}
    }

    async with httpx.AsyncClient() as ac:
        try:
            # Damos 40 segundos de margen porque la IA de imagen es lenta
            response = await ac.post(api_url, headers=headers, json=payload, timeout=40.0)
            
            if response.status_code == 200:
                # Convertimos el binario de la imagen a texto Base64
                img_str = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/jpeg;base64,{img_str}"
            else:
                print(f"Error HF Status: {response.status_code}")
                # Si falla, devolvemos un color sólido elegante con el nombre del plato
                return f"https://ui-avatars.com/api/?name={prompt_comida}&size=512&background=random"
        except Exception as e:
            print(f"Error en generador: {e}")
            return None

@app.get("/search")
async def get_recipe(query: str = Query(...)):
    try:
        # 1. Generar la receta con Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un Chef profesional. Responde únicamente en formato JSON con esta estructura: {'title': 'nombre', 'ingredients': ['lista'], 'instructions': 'texto paso a paso'}."
                },
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        receta = json.loads(chat_completion.choices[0].message.content)
        
        # 2. Generar la imagen (esperamos a que se cocine la IA)
        nombre_plato = receta.get('title', query)
        receta['image_url'] = await generar_imagen_profesional(nombre_plato)
        
        # Devolvemos una lista como espera tu App de Flutter
        return [receta]
        
    except Exception as e:
        print(f"Error General: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)