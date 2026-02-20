import os
import json
import google.generativeai as genai
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de Gemini 1.5 Flash
# Asegúrate de tener la variable GOOGLE_API_KEY en Render
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.get("/search")
async def buscar(query: str = Query(...)):
    prompt = f"""
    Actúa como un Chef Internacional. Genera una receta detallada para: {query}.
    Responde estrictamente en formato JSON con la siguiente estructura:
    {{
      "title": "Nombre del plato",
      "kcal": "número",
      "prot": "gramos",
      "ing": ["ingredientes con cantidades exactas"],
      "ins": ["pasos numerados"],
      "img_prompt": "high quality food photography, gourmet plating, {query}, detailed, 4k"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # Limpieza de la respuesta para obtener JSON puro
        raw_text = response.text
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0]
        
        data = json.loads(raw_text.strip())
        
        # Generación de imagen vía Pollinations (Motor Flux)
        img_url = f"[https://image.pollinations.ai/prompt/](https://image.pollinations.ai/prompt/){data['img_prompt'].replace(' ', '%20')}?model=flux&width=1024&height=768&nologo=true"

        return [{
            "title": data.get('title', '').upper(),
            "kcal": f"{data.get('kcal')} Kcal",
            "proteina": f"{data.get('prot')} Prot",
            "ingredients": data.get('ing', []),
            "instructions": data.get('ins', []),
            "image_url": img_url
        }]
    except Exception as e:
        return [{"title": "ERROR", "instructions": [str(e)], "image_url": ""}]

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)