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

# --- FASE 2: EL FOTÓGRAFO ESTRUCTURAL ACTIVADO ---
async def generar_imagen_avanzada(receta_data):
    api_url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    token = os.getenv("HF_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}
    
    nombre = receta_data.get("title", "Gourmet Dish")
    estructura = receta_data.get("visual_structure", "mixed")
    # Limpiamos ingredientes para el prompt visual
    ingredientes = ", ".join(receta_data.get("ingredients", [])[:4])

    # Definimos ángulo y luz según la estructura confirmada en el Paso 1
    if estructura == "separated_components":
        estilo_visual = "Flat lay, top-down view, ingredients arranged in separate, distinct sections on a large white plate."
    else:
        estilo_visual = "Professional 45-degree food photography, elegant plating."

    prompt_maestro = (
        f"Professional food photography of {nombre}. {estilo_visual} "
        f"Main components: {ingredientes}. "
        "Bright studio lighting, high contrast, vibrant natural colors, 8k resolution, "
        "ultra-detailed textures, clean white ceramic background, Michelin star presentation."
    )

    payload = {
        "inputs": prompt_maestro,
        "parameters": {
            "negative_prompt": "dark, moody, blurry, messy, mixed food, overlapping ingredients, text, watermark, low quality, pink shadows",
            "guidance_scale": 9.0,
            "num_inference_steps": 40
        }
    }

    async with httpx.AsyncClient() as ac:
        try:
            # Aumentamos el timeout a 80s porque SDXL es pesado
            response = await ac.post(api_url, headers=headers, json=payload, timeout=80.0)
            if response.status_code == 200:
                img_str = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/jpeg;base64,{img_str}"
        except Exception as e:
            print(f"Error en imagen: {e}")
        
        # Fallback si falla la IA
        return f"https://loremflickr.com/1024/768/food,{nombre.replace(' ', '')}"

@app.get("/search")
async def get_recipe_professional(query: str = Query(...)):
    try:
        system_prompt = """
        Eres un Chef Ejecutivo y Nutricionista. 
        Responde ÚNICAMENTE con un JSON en español.
        Clasifica en 'visual_structure': 'separated_components', 'bowl', 'layered' o 'mixed'.
        """

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Receta profesional completa para: {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        receta = json.loads(completion.choices[0].message.content)
        
        # AHORA SÍ: Generamos la imagen profesional usando los datos validados
        receta['image_url'] = await generar_imagen_avanzada(receta)
        
        return [receta]
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)