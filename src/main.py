import os
import json
import httpx
import base64
import asyncio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Configuración de CORS para que Flutter Web y Mobile no tengan bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialización de Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def generar_imagen_ia(prompt_comida):
    """
    Genera una imagen con estilo 'Vibrante Editorial'.
    Usa el nuevo Router de Hugging Face para evitar el error 410.
    """
    # URL ACTUALIZADA (Router estable)
    api_url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    token = os.getenv("HF_TOKEN")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # PROMPT DE ESTILO VIBRANTE PROFESIONAL
    prompt_estilizado = (
        f"Professional food photography of {prompt_comida}, vibrant colors, "
        "high saturation, macro lens, bright natural lighting, bokeh background, "
        "highly detailed textures, appetizing, 8k resolution, commercial food styling"
    )
    
    payload = {
        "inputs": prompt_estilizado,
        "parameters": {
            "negative_prompt": "dark, gloomy, blurry, low contrast, distorted, plastic, gray, dull, low quality",
            "guidance_scale": 9.0  # Mayor fidelidad al estilo vibrante
        },
        "options": {"wait_for_model": True, "use_cache": False}
    }

    async with httpx.AsyncClient() as ac:
        # AGOTAMOS LOS BUCLES: 3 intentos de 60 segundos cada uno
        for intento in range(3):
            try:
                print(f"--- Intento {intento + 1}: Generando imagen vibrante para {prompt_comida} ---")
                response = await ac.post(api_url, headers=headers, json=payload, timeout=60.0)
                
                if response.status_code == 200:
                    print("✅ ÉXITO: Imagen IA generada correctamente")
                    img_str = base64.b64encode(response.content).decode('utf-8')
                    return f"data:image/jpeg;base64,{img_str}"
                
                elif response.status_code == 503:
                    print(f"⏳ IA cargando (503). Reintentando en 15s...")
                    await asyncio.sleep(15)
                    continue
                else:
                    print(f"❌ Error de HF: {response.status_code} - {response.text}")
                    break
                    
            except Exception as e:
                print(f"⚠️ Excepción en generación de imagen: {str(e)}")
                await asyncio.sleep(2)
        
        # SI LA IA FALLA TRAS 3 INTENTOS: Respaldo de comida real (No gatos)
        print("🚀 Usando respaldo visual de LoremFlickr")
        return f"https://loremflickr.com/800/600/food,{prompt_comida.replace(' ', '')}/all"

@app.get("/search")
async def get_recipe(query: str = Query(...)):
    try:
        # 1. Generar la receta con Groq (Modelo Llama 3.3)
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un Chef experto en nutrición. Responde SOLO con un objeto JSON en español: {'title': str, 'ingredients': list, 'instructions': str}."
                },
                {"role": "user", "content": f"Dame una receta deliciosa y colorida de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        receta = json.loads(completion.choices[0].message.content)
        
        # 2. Generar la imagen vibrante
        nombre_plato = receta.get('title', query)
        receta['image_url'] = await generar_imagen_ia(nombre_plato)
        
        return [receta]
        
    except Exception as e:
        print(f"🔥 ERROR CRÍTICO: {e}")
        return [{"error": "No se pudo procesar la receta", "details": str(e)}]

if __name__ == "__main__":
    import uvicorn
    # Render asigna el puerto automáticamente
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)