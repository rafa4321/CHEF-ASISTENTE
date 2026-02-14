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

async def generar_imagen_ia(nombre_plato, ingredientes_lista):
    api_url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    token = os.getenv("HF_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}
    
    # PROMPT DE COMPOSICIÓN TRADICIONAL
    # Forzamos "separate portions" y "top-down view" para evitar mezclas raras
    prompt_final = (
        f"A top-down professional food photo of {nombre_plato}. "
        "The plate must show clearly separated portions of each ingredient: "
        f"{', '.join(ingredientes_lista[:5])}. "
        "Traditional plating, bright natural lighting, vibrant colors, "
        "high contrast, 8k resolution, clean white plate, professional culinary style."
    )
    
    payload = {
        "inputs": prompt_final,
        "parameters": {
            "negative_prompt": (
                "mixed food, stew, messy, dark, zoomed in, blurry, "
                "one single pile, overlapping ingredients, pink, neon, donut"
            ),
            "guidance_scale": 10.0, # Máximo rigor
            "num_inference_steps": 45
        },
        "options": {"wait_for_model": True, "use_cache": False}
    }

    async with httpx.AsyncClient() as ac:
        for intento in range(3):
            try:
                response = await ac.post(api_url, headers=headers, json=payload, timeout=80.0)
                if response.status_code == 200:
                    img_str = base64.b64encode(response.content).decode('utf-8')
                    return f"data:image/jpeg;base64,{img_str}"
                await asyncio.sleep(10)
            except: continue
        return f"https://loremflickr.com/800/600/food,{nombre_plato.replace(' ', '')}/all"

@app.get("/search")
async def get_recipe(query: str = Query(...)):
    try:
        # INSTRUCCIÓN DE ESCALA: Forzamos a Groq a calcular cantidades según la búsqueda
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Eres un Chef experto. Calcula las cantidades exactas según el número de personas solicitado. "
                        "Responde SOLO JSON: {'title': str, 'ingredients': list, 'instructions': str}. "
                        "Para platos tradicionales, respeta la presentación clásica de ingredientes separados."
                    )
                },
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        receta = json.loads(completion.choices[0].message.content)
        receta['image_url'] = await generar_imagen_ia(receta['title'], receta['ingredients'])
        
        return [receta]
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)