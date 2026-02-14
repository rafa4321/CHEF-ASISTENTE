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
    Versión 'Master Chef': Desglosa el plato por componentes para 
    asegurar que aparezcan todos (arroz, granos, carne, etc.)
    """
    api_url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    token = os.getenv("HF_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}
    
    ingredientes_raw = " ".join(ingredientes_lista).lower()
    prompt_min = prompt_comida.lower()
    
    # --- LÓGICA DE COMPOSICIÓN ESTRICTA POR PLATO ---
    detalles_plato = ""
    
    if "pabellon" in prompt_min:
        detalles_plato = (
            "Traditional plate with distinct portions of: white rice, black beans (caraotas), "
            "shredded beef (carne mechada), and golden fried plantain slices (tajadas). "
        )
        if "caballo" in prompt_min:
            detalles_plato += "A perfect sunny-side up fried egg on top. "
            
    elif any(x in ingredientes_raw or x in prompt_min for x in ["corocoro", "pescado"]):
        detalles_plato = (
            "A whole fried crispy fish (Corocoro) as the main star, served with "
            "fresh salad and lemon wedges on the side. No rice balls. "
        )
    
    # Prompt final descriptivo para evitar que la IA 'resuma' el plato
    prompt_final = (
        f"Authentic high-end food photography of {prompt_comida}. "
        f"The plate must include: {detalles_plato}. "
        "Professional plating, natural lighting, 8k resolution, sharp focus, "
        "appetizing real textures, cinematic composition."
    )
    
    payload = {
        "inputs": prompt_final,
        "parameters": {
            "negative_prompt": (
                "only meat, missing rice, missing beans, blurry ingredients, "
                "pink, donut, circle, abstract, surreal, cartoon, drawing, "
                "low quality, plastic texture, messy, deformed, yellow rice on fish"
            ),
            "guidance_scale": 9.0, # Mayor rigor para seguir las instrucciones
            "num_inference_steps": 40
        },
        "options": {"wait_for_model": True, "use_cache": False}
    }

    async with httpx.AsyncClient() as ac:
        for intento in range(3):
            try:
                print(f"--- Intento {intento + 1}: Componiendo plato completo para {prompt_comida} ---")
                response = await ac.post(api_url, headers=headers, json=payload, timeout=65.0)
                
                if response.status_code == 200:
                    print("✅ ÉXITO: Imagen compuesta correctamente")
                    img_str = base64.b64encode(response.content).decode('utf-8')
                    return f"data:image/jpeg;base64,{img_str}"
                
                elif response.status_code == 503:
                    print(f"⏳ IA despertando... esperando 15s")
                    await asyncio.sleep(15)
                else:
                    print(f"❌ Error de API: {response.status_code}")
                    break
            except Exception as e:
                print(f"⚠️ Error: {e}")
        
        return f"https://loremflickr.com/800/600/food,{prompt_comida.replace(' ', '')}/all"

@app.get("/search")
async def get_recipe(query: str = Query(...)):
    try:
        # 1. Groq genera la estructura de la receta
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un Chef Estrella Michelin. Responde exclusivamente en JSON: {'title': str, 'ingredients': list, 'instructions': str}."
                },
                {"role": "user", "content": f"Dame la receta tradicional completa de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        receta = json.loads(completion.choices[0].message.content)
        
        # 2. Generamos la imagen pasando el título y los ingredientes para la 'lista de chequeo'
        receta['image_url'] = await generar_imagen_ia(
            receta.get('title', query), 
            receta.get('ingredients', [])
        )
        
        return [receta]
        
    except Exception as e:
        print(f"🔥 Error Crítico: {e}")
        return [{"error": str(e)}]

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)