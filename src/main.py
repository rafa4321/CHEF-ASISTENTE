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
    # Usamos el router actualizado para evitar el error 410
    api_url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    token = os.getenv("HF_TOKEN")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # PROMPT DE REALISMO ESTRICTO
    # Enfocado en texturas reales, vapor y fotografía de restaurante real.
    prompt_final = (
        f"Hyper-realistic professional photography of {prompt_comida}, "
        "authentic traditional dish, 8k dslr, cinematic lighting, "
        "detailed food textures, natural colors, steam, restaurant table setting, "
        "sharp focus, appetizing real food"
    )
    
    payload = {
        "inputs": prompt_final,
        "parameters": {
            # El Negative Prompt bloquea lo que vimos en tu captura (colores rosados, formas de dona)
            "negative_prompt": (
                "pink, purple, neon, donut, circle, abstract, surreal, "
                "cartoon, anime, drawing, blurry, low quality, deformed food, "
                "plastic texture, artistic, conceptual"
            ),
            "guidance_scale": 7.0, # Balance perfecto entre seguir el texto y realismo
            "num_inference_steps": 35
        },
        "options": {"wait_for_model": True, "use_cache": False}
    }

    async with httpx.AsyncClient() as ac:
        for intento in range(3):
            try:
                print(f"--- Intento {intento + 1}: Generando foto REALISTA para {prompt_comida} ---")
                response = await ac.post(api_url, headers=headers, json=payload, timeout=60.0)
                
                if response.status_code == 200:
                    img_str = base64.b64encode(response.content).decode('utf-8')
                    return f"data:image/jpeg;base64,{img_str}"
                
                elif response.status_code == 503:
                    await asyncio.sleep(15)
                    continue
                else:
                    print(f"Error HF: {response.status_code}")
                    break
            except Exception as e:
                print(f"Error: {e}")
        
        # Respaldo visual de comida real si la IA falla
        return f"https://loremflickr.com/800/600/food,{prompt_comida.replace(' ', '')}/all"

@app.get("/search")
async def get_recipe(query: str = Query(...)):
    try:
        # Groq genera la receta detallada
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un Chef especializado en cocina tradicional. Responde SOLO JSON en español: {'title': str, 'ingredients': list, 'instructions': str}."
                },
                {"role": "user", "content": f"Receta tradicional de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        receta = json.loads(completion.choices[0].message.content)
        
        # Generamos la imagen basada en el título real de la receta
        receta['image_url'] = await generar_imagen_ia(receta.get('title', query))
        
        return [receta]
        
    except Exception as e:
        print(f"Error: {e}")
        return [{"error": str(e)}]

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)