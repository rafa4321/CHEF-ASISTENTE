import os
import json
from google import genai
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializamos el cliente
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

@app.get("/search")
async def buscar_receta(query: str = Query(...)):
    prompt = (
        f"Genera una receta de cocina para: {query}. "
        "Responde ESTRICTAMENTE en formato JSON con esta estructura: "
        '{"title": "Nombre", "kcal": "valor", "proteina": "valor", '
        '"ingredients": ["item1", "item2"], "instructions": ["paso1", "paso2"], '
        '"img_prompt": "comida gourmet de tipo {query}"}'
    )
    
    try:
        # CAMBIO CLAVE: Usamos el nombre del modelo estable actual
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp", 
            contents=prompt
        )
        
        # Limpieza robusta del JSON
        texto_limpio = response.text.strip()
        if "```json" in texto_limpio:
            texto_limpio = texto_limpio.split("```json")[1].split("```")[0].strip()
        elif "```" in texto_limpio:
            texto_limpio = texto_limpio.split("```")[1].split("```")[0].strip()
            
        data = json.loads(texto_limpio)
        
        # Generador de imagen gratuito
        img_url = f"https://image.pollinations.ai/prompt/{data['img_prompt'].replace(' ', '%20')}?model=flux&width=1024&height=1024&nologo=true"

        return [{
            "title": data.get('title', 'Receta').upper(),
            "kcal": f"{data.get('kcal', '0')} Kcal",
            "proteina": f"{data.get('proteina', '0')} Prot",
            "ingredients": data.get('ingredients', []),
            "instructions": data.get('instructions', []),
            "image_url": img_url
        }]
    except Exception as e:
        return [{"error": f"Error: {str(e)}"}]

@app.get("/")
async def root():
    return {"mensaje": "Chef Asistente API Online"}