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

# Inicializar Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def generar_imagen_profesional(prompt_comida):
    """
    Genera imagen con Hugging Face. Si falla, usa un respaldo de comida real.
    """
    # Modelo altamente disponible y estable
    api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    token = os.getenv("HF_TOKEN")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": f"Professional food photo, {prompt_comida}, gourmet presentation, studio lighting, 4k",
        "options": {"wait_for_model": True} 
    }

    async with httpx.AsyncClient() as ac:
        try:
            # Intentar hasta 2 veces si el modelo está cargando
            for intento in range(2):
                response = await ac.post(api_url, headers=headers, json=payload, timeout=35.0)
                
                if response.status_code == 200:
                    img_str = base64.b64encode(response.content).decode('utf-8')
                    return f"data:image/jpeg;base64,{img_str}"
                
                elif response.status_code == 503: # Modelo despertando
                    await asyncio.sleep(10)
                    continue
                else:
                    break
            
            # RESPALDO DE COMIDA REAL (Si la IA falla, esto siempre funciona)
            return f"https://loremflickr.com/800/600/food,{prompt_comida.replace(' ', '')}/all"

        except Exception as e:
            print(f"Error Generador: {e}")
            return f"https://ui-avatars.com/api/?name={prompt_comida}&size=512"

@app.get("/search")
async def get_recipe(query: str = Query(...)):
    try:
        # 1. Generar receta con Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un Chef Gourmet. Responde SOLO JSON: {'title': str, 'ingredients': list, 'instructions': str}."
                },
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        receta = json.loads(chat_completion.choices[0].message.content)
        
        # 2. Generar imagen (IA o Respaldo)
        receta['image_url'] = await generar_imagen_profesional(receta.get('title', query))
        
        return [receta]
        
    except Exception as e:
        print(f"Error en servidor: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)