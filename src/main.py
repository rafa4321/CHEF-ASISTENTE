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

# Inicializamos el cliente con la API KEY de Render
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

@app.get("/search")
async def buscar_receta(query: str = Query(...)):
    prompt = (
        f"Genera una receta de cocina para: {query}. "
        "Responde exclusivamente en formato JSON: "
        '{"title": "Nombre", "kcal": "valor", "proteina": "valor", '
        '"ingredients": ["item1"], "instructions": ["paso1"], '
        '"img_prompt": "comida gourmet de {query}"}'
    )
    
    try:
        # NOMBRE EXACTO: Sin el prefijo 'models/' porque la librería ya lo asume
        # Usamos 'gemini-1.5-flash' que es el más estable y universal
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        
        # Limpiamos posibles marcas de markdown del JSON
        texto = response.text.strip()
        if "```json" in texto:
            texto = texto.split("```json")[1].split("```")[0].strip()
        elif "```" in texto:
            texto = texto.split("```")[1].split("```")[0].strip()
            
        data = json.loads(texto)
        
        img_url = f"https://image.pollinations.ai/prompt/{data['img_prompt'].replace(' ', '%20')}?model=flux&nologo=true"

        return [{
            "title": data.get('title', 'Receta').upper(),
            "kcal": f"{data.get('kcal', '0')} Kcal",
            "proteina": f"{data.get('proteina', '0')} Prot",
            "ingredients": data.get('ingredients', []),
            "instructions": data.get('instructions', []),
            "image_url": img_url
        }]
    except Exception as e:
        # Esto nos dirá exactamente qué modelo está pidiendo Google si falla
        return [{"error": f"Error técnico: {str(e)}"}]

@app.get("/")
async def root():
    return {"mensaje": "Chef Asistente API lista"}