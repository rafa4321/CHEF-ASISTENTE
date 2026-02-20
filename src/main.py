import os
import json
import google.generativeai as genai
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuración de CORS para conectar con la App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.get("/search")
async def buscar(query: str = Query(...)):
    prompt = f"""
    Eres un Chef de clase mundial. Genera una receta para: {query}. 
    Responde ÚNICAMENTE en formato JSON con esta estructura exacta:
    {{
      "title": "nombre",
      "kcal": "valor",
      "proteina": "valor",
      "ingredients": ["lista"],
      "instructions": ["pasos"],
      "img_prompt": "gourmet professional food photography of {query}, 4k"
    }}
    """
    try:
        response = model.generate_content(prompt)
        # Limpieza de markdown
        txt = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(txt)
        
        # Generador de imagen Flux vía Pollinations
        img_url = f"https://image.pollinations.ai/prompt/{data['img_prompt'].replace(' ', '%20')}?model=flux&width=1024&height=768&nologo=true"

        return [{
            "title": data.get('title', '').upper(),
            "kcal": f"{data.get('kcal', '---')} Kcal",
            "proteina": f"{data.get('proteina', '---')} Prot",
            "ingredients": data.get('ingredients', []),
            "instructions": data.get('instructions', []),
            "image_url": img_url
        }]
    except Exception as e:
        return [{"title": "ERROR", "instructions": [str(e)], "image_url": ""}]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))