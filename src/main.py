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

async def generar_imagen_ia(prompt_comida, ingredientes_lista):
    """
    Analiza la receta y genera una imagen coherente.
    Si es un pez como el Corocoro, fuerza la imagen de un pescado.
    """
    api_url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    token = os.getenv("HF_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Lógica de coherencia: Detectar si es pescado, carne o ave
    contexto_visual = ""
    ingredientes_raw = " ".join(ingredientes_lista).lower()
    prompt_min = prompt_comida.lower()

    if any(x in ingredientes_raw or x in prompt_min for x in ["pescado", "pez", "corocoro", "pargo", "carite"]):
        contexto_visual = "A whole crispy fried fish on a plate, traditional seafood presentation, "
    elif any(x in ingredientes_raw or x in prompt_min for x in ["carne", "mechada", "pabellon"]):
        contexto_visual = "Shredded beef meat with traditional sides, "
    elif any(x in ingredientes_raw or x in prompt_min for x in ["pollo", "gallina"]):
        contexto_visual = "Roasted chicken dish, "

    # Prompt final ultra-específico
    prompt_final = (
        f"Authentic professional food photography of {contexto_visual}{prompt_comida}, "
        "on a restaurant table, 8k dslr, cinematic lighting, sharp focus, "
        "highly detailed food textures, natural colors, appetizing"
    )
    
    payload = {
        "inputs": prompt_final,
        "parameters": {
            # Bloqueamos arroz, donas y colores raros para platos de pescado/carne
            "negative_prompt": (
                "rice, grains, yellow rice, donut, pink, purple, neon, circle, "
                "abstract, surreal, cartoon, drawing, low quality, plastic texture, "
                "deformed, messy, blurry"
            ),
            "guidance_scale": 7.5,
            "num_inference_steps": 30
        },
        "options": {"wait_for_model": True, "use_cache": False}
    }

    async with httpx.AsyncClient() as ac:
        for intento in range(3):
            try:
                print(f"--- Intento {intento + 1}: Generando imagen coherente para {prompt_comida} ---")
                response = await ac.post(api_url, headers=headers, json=payload, timeout=60.0)
                
                if response.status_code == 200:
                    print("✅ ÉXITO: Imagen coherente generada")
                    img_str = base64.b64encode(response.content).decode('utf-8')
                    return f"data:image/jpeg;base64,{img_str}"
                
                elif response.status_code == 503:
                    await asyncio.sleep(15)
                    continue
                else:
                    print(f"❌ Error HF {response.status_code}: {response.text}")
                    break
            except Exception as e:
                print(f"⚠️ Error: {e}")
        
        # Respaldo de seguridad
        return f"https://loremflickr.com/800/600/food,{prompt_comida.replace(' ', '')}/all"

@app.get("/search")
async def get_recipe(query: str = Query(...)):
    try:
        # 1. Groq genera la receta (texto)
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un Chef experto en gastronomía auténtica. Responde SOLO JSON en español: {'title': str, 'ingredients': list, 'instructions': str}."
                },
                {"role": "user", "content": f"Receta tradicional de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        receta = json.loads(completion.choices[0].message.content)
        
        # 2. Generar imagen pasando la lista de ingredientes para evitar confusiones
        receta['image_url'] = await generar_imagen_ia(
            receta.get('title', query), 
            receta.get('ingredients', [])
        )
        
        return [receta]
        
    except Exception as e:
        print(f"🔥 ERROR: {e}")
        return [{"error": str(e)}]

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)