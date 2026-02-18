import os
import json
import httpx
import base64
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def generar_foto_profesional(prompt_visual):
    # Usamos FAL.AI con el modelo FLUX.1 [Dev] para calidad máxima
    url = "https://fal.run/fal-ai/flux/dev"
    headers = {
        "Authorization": f"Key {os.getenv('FAL_KEY')}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": f"Professional food photography of {prompt_visual}, gourmet plating, high resolution, 4k, realistic textures, cinematic lighting",
        "image_size": "landscape_4_3",
        "num_inference_steps": 28,
        "guidance_scale": 3.5
    }

    try:
        async with httpx.AsyncClient() as ac:
            # Fal.ai es ultra rápido, bajamos el timeout a 30s
            response = await ac.post(url, headers=headers, json=payload, timeout=30.0)
            
            if response.status_code == 200:
                data = response.json()
                # Fal nos da una URL directa de alta velocidad
                return data.get("images", [{}])[0].get("url", "")
            else:
                print(f"Error Fal.ai: {response.status_code} - {response.text}")
                return ""
    except Exception as e:
        print(f"Excepción en Fal.ai: {e}")
        return ""

@app.get("/search")
async def buscar(query: str = Query(...)):
    try:
        # 1. LLAMA 3 genera la receta y el PROMPT VISUAL
        system_prompt = """
        Eres un Chef Estrella Michelin. Responde en JSON estricto:
        {
          "title": "nombre",
          "kcal": "valor",
          "prot": "valor",
          "ing": ["lista"],
          "ins": ["pasos"],
          "visual_prompt": "descripción detallada en inglés para una IA de imagen"
        }
        """
        
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)
        
        # 2. Generamos la imagen con el prompt visual de Llama
        # Esto asegura que si pides Asado Negro, se pida una imagen de carne oscura.
        foto_url = await generar_foto_profesional(res.get("visual_prompt", query))

        return [{
            "title": res.get("title", "RECETA").upper(),
            "kcal": f"{res.get('kcal', '---')} Kcal",
            "proteina": f"{res.get('prot', '---')} Prot",
            "ingredients": res.get("ing", []),
            "instructions": res.get("ins", []),
            "image_url": foto_url
        }]
    except Exception as e:
        print(f"Error Crítico: {e}")
        return [{"title": "ERROR", "instructions": [str(e)], "image_url": ""}]