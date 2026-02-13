import os
import json
import httpx
import base64
import asyncio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Configuración de CORS profesional
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar cliente de Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def generar_imagen_ia(prompt_comida):
    """
    Intenta generar una imagen con IA de alta calidad. 
    Si falla tras varios reintentos, usa el respaldo de comida real.
    """
    # Modelo XL de alta definición para resultados "Premium"
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    token = os.getenv("HF_TOKEN")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": f"Gourmet professional food photography of {prompt_comida}, michelin star presentation, 8k resolution, highly detailed, cinematic lighting",
        "options": {"wait_for_model": True, "use_cache": False}
    }

    async with httpx.AsyncClient() as ac:
        for intento in range(3):  # 3 intentos para forzar a la IA a despertar
            try:
                print(f"--- Intento {intento + 1}: Generando imagen para {prompt_comida} ---")
                # Aumentamos a 60 segundos porque los modelos XL son pesados
                response = await ac.post(api_url, headers=headers, json=payload, timeout=60.0)
                
                if response.status_code == 200:
                    print("✅ ÉXITO: Imagen generada por IA")
                    img_str = base64.b64encode(response.content).decode('utf-8')
                    return f"data:image/jpeg;base64,{img_str}"
                
                elif response.status_code == 503:
                    print(f"⏳ IA cargando (503). Esperando 15s... (Intento {intento + 1}/3)")
                    await asyncio.sleep(15)
                else:
                    print(f"❌ Error de HF: {response.status_code} - {response.text}")
                    break
            except Exception as e:
                print(f"⚠️ Error en intento {intento + 1}: {str(e)}")
        
        # SI TODO FALLA: Respaldo de comida real (LoremFlickr)
        print("🚀 Usando respaldo de LoremFlickr para no dejar vacía la App")
        return f"https://loremflickr.com/800/600/food,{prompt_comida.replace(' ', '')}/all"

@app.get("/search")
async def get_recipe(query: str = Query(...)):
    try:
        # 1. Generar receta con el modelo más potente de Llama
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un Chef Estrella Michelin. Responde exclusivamente en JSON con: {'title': str, 'ingredients': list, 'instructions': str}. Todo en español."
                },
                {"role": "user", "content": f"Receta gourmet de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        receta = json.loads(completion.choices[0].message.content)
        
        # 2. Generar la imagen profesional
        nombre_plato = receta.get('title', query)
        receta['image_url'] = await generar_imagen_ia(nombre_plato)
        
        return [receta]
        
    except Exception as e:
        print(f"🔥 ERROR CRÍTICO EN SERVIDOR: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)