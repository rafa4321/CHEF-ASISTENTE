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
    # Usamos FAL.AI con FLUX.1 [Dev] para calidad máxima
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
            response = await ac.post(url, headers=headers, json=payload, timeout=40.0)
            if response.status_code == 200:
                data = response.json()
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
        # INSTRUCCIONES ESTRICTAS PARA RECETA PROLIJA
        system_prompt = """
        Eres un Chef Ejecutivo Estrella Michelin. Responde exclusivamente en JSON.
        
        REGLAS PARA LA RECETA:
        1. Cantidades exactas: Usa kg, gr, tazas, cucharaditas.
        2. Prolijidad: Los ingredientes deben detallar el corte (picado finamente, en rodajas).
        3. Fases: Las instrucciones deben dividirse en fases (Sellado, Marinado, Cocción).
        
        JSON STRUCTURE:
        {
          "title": "NOMBRE DEL PLATO",
          "kcal": "número total",
          "prot": "gramos",
          "ing": ["lista detallada de ingredientes con cantidades"],
          "ins": ["fase 1: descripción", "fase 2: descripción", "fase 3: descripción"],
          "visual_prompt": "detailed technical food description in English for AI image generation"
        }
        """
        
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)
        
        # Generamos la imagen profesional usando el visual_prompt del Chef
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
        print(f"Error: {e}")
        return [{"title": "ERROR", "instructions": [str(e)], "image_url": ""}]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))