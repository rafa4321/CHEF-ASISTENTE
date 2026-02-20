import os
import json
import google.generativeai as genai
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Conexión limpia para Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración única: Gemini 1.5 Flash
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.get("/search")
async def buscar(query: str = Query(...)):
    print(f"Buscando receta para: {query}") # Log para Render
    
    prompt = f"""
    Genera una receta para: {query}. Responde SOLO en JSON:
    {{
      "title": "nombre",
      "kcal": "valor",
      "proteina": "valor",
      "ingredients": ["lista"],
      "instructions": ["pasos"],
      "img_prompt": "gourmet food photography of {query}, high resolution"
    }}
    """
    try:
        response = model.generate_content(prompt)
        txt = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(txt)
        
        # Generación de imagen con Pollinations (NO usa Hugging Face)
        img_url = f"https://image.pollinations.ai/prompt/{data['img_prompt'].replace(' ', '%20')}?model=flux&nologo=true"

        return [{
            "title": data['title'].upper(),
            "kcal": f"{data['kcal']} Kcal",
            "proteina": f"{data['proteina']} Prot",
            "ingredients": data['ingredients'],
            "instructions": data['instructions'],
            "image_url": img_url
        }]
    except Exception as e:
        print(f"Error detectado: {e}")
        return [{"title": "ERROR", "instructions": [str(e)], "image_url": ""}]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))