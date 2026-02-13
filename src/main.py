import os
import json
import httpx
import base64
import asyncio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def generar_imagen_ia(prompt_comida):
    # NUEVA URL DE HUGGING FACE (Corregida según el error 410 de tus logs)
    api_url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    token = os.getenv("HF_TOKEN")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": f"Gourmet professional food photography of {prompt_comida}, michelin star presentation, 8k, cinematic lighting",
        "parameters": {"negative_prompt": "ugly, blurry, low quality"},
        "options": {"wait_for_model": True}
    }

    async with httpx.AsyncClient() as ac:
        # AGOTAMOS LOS BUCLES: 3 intentos con la nueva URL
        for intento in range(3):
            try:
                print(f"--- Intento {intento + 1}: Contactando con el NUEVO Router de HF para {prompt_comida} ---")
                response = await ac.post(api_url, headers=headers, json=payload, timeout=60.0)
                
                if response.status_code == 200:
                    print("✅ ÉXITO TOTAL: Imagen generada por IA")
                    img_str = base64.b64encode(response.content).decode('utf-8')
                    return f"data:image/jpeg;base64,{img_str}"
                
                elif response.status_code == 503:
                    print(f"⏳ IA despertando... esperando 15s (Intento {intento + 1}/3)")
                    await asyncio.sleep(15)
                else:
                    print(f"❌ Error detallado: {response.status_code} - {response.text}")
                    # Si el error es de cuota (429), no seguimos intentando
                    if response.status_code == 429: break 
            
            except Exception as e:
                print(f"⚠️ Excepción en bucle: {str(e)}")
        
        # Respaldo solo si la IA realmente no responde tras agotar intentos
        return f"https://loremflickr.com/800/600/food,{prompt_comida.replace(' ', '')}/all"

@app.get("/search")
async def get_recipe(query: str = Query(...)):
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Chef Gourmet. Responde SOLO JSON: {'title': str, 'ingredients': list, 'instructions': str}. Idioma: Español."},
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        receta = json.loads(completion.choices[0].message.content)
        receta['image_url'] = await generar_imagen_ia(receta.get('title', query))
        return [receta]
    except Exception as e:
        print(f"🔥 ERROR: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)