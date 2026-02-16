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

async def generar_imagen_ia(descripcion_plato):
    """Genera una imagen gourmet única usando Stable Diffusion XL"""
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    # Prompt técnico para evitar que la IA dibuje cosas raras
    prompt_completo = f"Gourmet professional food photography of {descripcion_plato}, elegant plating, neutral background, 8k, highly detailed, studio lighting."
    
    try:
        async with httpx.AsyncClient() as ac:
            response = await ac.post(api_url, headers=headers, json={"inputs": prompt_completo}, timeout=60.0)
            if response.status_code == 200:
                return f"data:image/jpeg;base64,{base64.b64encode(response.content).decode('utf-8')}"
    except Exception as e:
        print(f"Error imagen: {e}")
    return "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"

@app.get("/search")
async def buscar_receta_profesional(query: str = Query(...)):
    try:
        system_prompt = """
        Eres un Chef Estrella Michelin experto en cocina internacional.
        TU OBJETIVO: Dar recetas extremadamente detalladas y precisas.
        
        REGLAS:
        1. INGREDIENTES: Cantidades exactas (gramos, mililitros, unidades).
        2. PREPARACIÓN: Detalla cada técnica (ej: 'sofreír hasta caramelizar', 'fuego corona', 'reposo de 10 min').
        3. FORMATO: Responde SIEMPRE en este JSON:
        {
          "title": "NOMBRE DEL PLATO",
          "kcal": "850",
          "prot": "45g",
          "ing": ["500g de Carne Mechada", "2 tazas de Arroz"],
          "ins": ["Paso 1 detallado...", "Paso 2 detallado...", "Paso 3 detallado..."]
        }
        """

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Receta detallada de: {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        data = json.loads(completion.choices[0].message.content)
        
        # Generamos la imagen real basada en el título que dio la IA
        url_ia = await generar_imagen_ia(data.get("title", query))

        return [{
            "title": data.get("title", query).upper(),
            "kcal": data.get("kcal", "---"),
            "proteina": data.get("prot", "---"),
            "ingredients": data.get("ing", []),
            "instructions": data.get("ins", []), # Se envía como lista detallada
            "image_url": url_ia
        }]
    except Exception as e:
        return [{"title": "ERROR", "instructions": [str(e)], "ingredients": []}]

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)