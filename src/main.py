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

# --- FUNCIÓN DE IMAGEN PROFESIONAL (FASE 2) ---
async def generar_imagen_ia(receta_data):
    # Usamos Hugging Face para generar imágenes de alta calidad
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    
    nombre = receta_data.get("title", "Plato Gourmet")
    estructura = receta_data.get("visual_structure", "mixed")
    
    # Prompt técnico para evitar platos oscuros o mezclados
    estilo = "Top-down view, bright studio lighting, white plate, Michelin star plating."
    if estructura == "separated_components":
        estilo += " Ingredients served in separate portions, neat arrangement."

    prompt = f"Professional food photography of {nombre}. {estilo} 8k resolution, vibrant colors."
    
    try:
        async with httpx.AsyncClient() as ac:
            response = await ac.post(api_url, headers=headers, json={"inputs": prompt}, timeout=60.0)
            if response.status_code == 200:
                img_base64 = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/jpeg;base64,{img_base64}"
    except:
        pass
    
    # Fallback si falla la generación
    return f"https://loremflickr.com/800/600/food,{nombre.replace(' ', '')}"

@app.get("/search")
async def get_recipe_professional(query: str = Query(...)):
    try:
        system_prompt = """
        Eres un Chef Estrella Michelin. Genera la receta en JSON.
        IMPORTANTE: 'ingredients' y 'steps' deben ser LISTAS de strings.
        'visual_structure' debe ser 'separated_components' o 'mixed'.
        """

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Receta para: {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        receta = json.loads(completion.choices[0].message.content)
        
        # Generar la imagen real
        receta['image_url'] = await generar_imagen_ia(receta)
        
        # Esto asegura que tu App de Flutter reciba la lista que espera
        return [receta]
        
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)