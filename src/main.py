import os
import json
import google.generativeai as genai
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuración de CORS para permitir conexión desde Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de Gemini 1.5 Flash
# Importante: Debes tener la variable GOOGLE_API_KEY en Render
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.get("/search")
async def buscar(query: str = Query(...)):
    # Prompt optimizado para respuesta JSON pura y rápida
    prompt = f"""
    Actúa como un Chef Internacional experto.
    Genera una receta para: {query}.
    Responde ÚNICAMENTE en formato JSON con esta estructura exacta:
    {{
      "title": "Nombre del plato",
      "kcal": "número",
      "proteina": "gramos",
      "ingredients": ["lista de ingredientes"],
      "instructions": ["pasos detallados"],
      "img_prompt": "professional gourmet food photography, {query}, high resolution, 4k"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # Limpieza de posibles etiquetas de markdown
        txt = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(txt)
        
        # Generador de imagen Flux (vía Pollinations) - Rápido y estable
        img_url = f"https://image.pollinations.ai/prompt/{data['img_prompt'].replace(' ', '%20')}?model=flux&nologo=true"

        # Retornamos una lista para mantener compatibilidad con tu RecipeService actual
        return [{
            "title": data.get('title', '').upper(),
            "kcal": f"{data.get('kcal', '---')} Kcal",
            "proteina": f"{data.get('proteina', '---')} Prot",
            "ingredients": data.get('ingredients', []),
            "instructions": data.get('instructions', []),
            "image_url": img_url
        }]
    except Exception as e:
        print(f"Error: {e}")
        return [{"title": "ERROR", "instructions": [str(e)], "image_url": ""}]

if __name__ == "__main__":
    import uvicorn
    # Render usa la variable de entorno PORT
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)