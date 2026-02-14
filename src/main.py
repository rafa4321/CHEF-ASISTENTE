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
    """
    Genera una imagen con VISTA FRONTAL, alta luminosidad y composición completa.
    """
    api_url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    token = os.getenv("HF_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Limpiamos la lista de ingredientes para que no haya errores
    ingredientes_texto = ", ".join([str(i) for i in ingredientes_lista[:5]])
    
    # PROMPT: Vista frontal (Top-down o Eye-level), Iluminación de estudio brillante
    prompt_final = (
        f"A top-down professional food photograph of a full plate of {nombre_plato}. "
        f"The plate contains: {ingredientes_texto}. "
        "High-angle shot, bright studio lighting, white background, "
        "vibrant colors, sharp focus, 8k resolution, commercial food photography, "
        "clean plating, high contrast, airy and bright."
    )
    
    payload = {
        "inputs": prompt_final,
        "parameters": {
            "negative_prompt": (
                "dark, moody, shadows, zoomed in, cropped, blurry, "
                "messy, low quality, plastic, distorted, text, code, "
                "url, website, watermark, purple lighting"
            ),
            "guidance_scale": 9.0,
            "num_inference_steps": 40
        },
        "options": {"wait_for_model": True, "use_cache": False}
    }

    async with httpx.AsyncClient() as ac:
        for intento in range(3):
            try:
                response = await ac.post(api_url, headers=headers, json=payload, timeout=75.0)
                if response.status_code == 200:
                    img_str = base64.b64encode(response.content).decode('utf-8')
                    return f"data:image/jpeg;base64,{img_str}"
                await asyncio.sleep(10)
            except:
                continue
        return f"https://loremflickr.com/800/600/food,{nombre_plato.replace(' ', '')}/all"

@app.get("/search")
async def get_recipe(query: str = Query(...)):
    try:
        # IMPORTANTE: Forzamos a Groq a ser muy estricto con el JSON
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un Chef Profesional. Responde ÚNICAMENTE con un objeto JSON válido. NO incluyas explicaciones ni URLs. Formato: {'title': 'nombre', 'ingredients': ['item1', 'item2'], 'instructions': 'pasos'}"
                },
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        # Limpiamos cualquier residuo de texto antes de cargar el JSON
        contenido = completion.choices[0].message.content.strip()
        receta = json.loads(contenido)
        
        # Generamos la imagen con la nueva configuración de luz y ángulo
        receta['image_url'] = await generar_imagen_ia(receta['title'], receta['ingredients'])
        
        return [receta]
    except Exception as e:
        print(f"Error: {e}")
        return [{"error": "Error al generar la receta"}]

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)