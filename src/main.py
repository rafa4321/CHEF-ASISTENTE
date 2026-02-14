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

# PASO 1: Validación de Identidad Gastronómica
async def generar_imagen_ia(receta_data):
    # Placeholder para no gastar cuota mientras validamos los datos
    nombre = receta_data.get("title", "Receta")
    return f"https://loremflickr.com/800/600/food,{nombre.replace(' ', '')}"

@app.get("/search")
async def get_recipe_professional(query: str = Query(...)):
    try:
        print(f"--- Iniciando búsqueda profesional para: {query} ---")
        
        system_prompt = """
        Eres un Chef Ejecutivo Estrella Michelin y Nutricionista. 
        Tu salida debe ser un JSON estricto en español.
        Calcula las cantidades según el número de personas mencionado en el query.
        
        Estructura Visual Obligatoria:
        - 'separated_components': Si el plato lleva ingredientes sin mezclar (ej. Pabellón, Corocoro frito con acompañantes).
        - 'bowl': Sopas o ensaladas.
        - 'mixed': Arroces compuestos o salteados.

        Formato JSON:
        {
            "title": "Nombre del plato",
            "description": "Descripción apetitosa",
            "ingredients": ["lista con cantidades exactas"],
            "steps": ["pasos detallados"],
            "plating_guide": "Instrucciones de emplatado profesional",
            "chef_tips": ["2 secretos del chef"],
            "nutrition": { "calories": "kcal", "protein": "g", "carbs": "g", "fat": "g" },
            "visual_structure": "una de las 3 opciones anteriores"
        }
        """

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Receta completa de: {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        receta = json.loads(completion.choices[0].message.content)
        
        # Agregamos el placeholder de imagen
        receta['image_url'] = await generar_imagen_ia(receta)
        
        print("✅ Receta generada con éxito")
        return [receta]
        
    except Exception as e:
        print(f"❌ Error en Step 1: {str(e)}")
        return [{"error": str(e)}]

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)