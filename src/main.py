import os
import json
import google.generativeai as genai  # Librería ESTABLE
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración estable
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

@app.get("/search")
async def buscar_receta(query: str = Query(...)):
    prompt = (
        f"Genera una receta para: {query}. "
        "Responde solo en JSON: "
        '{"title": "Nombre", "kcal": "valor", "proteina": "valor", '
        '"ingredients": ["item1"], "instructions": ["paso1"], '
        '"img_prompt": "comida gourmet de {query}"}'
    )
    
    try:
        # Usamos el modelo estable
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        # Verificamos si hay texto antes de usar .strip()
        if not response or not response.text:
            return [{"error": "Google no devolvió texto"}]
            
        texto = response.text.strip()
        # Limpieza de markdown
        if "```json" in texto:
            texto = texto.split("```json")[1].split("```")[0].strip()
            
        data = json.loads(texto)
        img_url = f"[https://image.pollinations.ai/prompt/](https://image.pollinations.ai/prompt/){data.get('img_prompt', query).replace(' ', '%20')}?model=flux&nologo=true"

        return [{
            "title": data.get('title', query).upper(),
            "kcal": f"{data.get('kcal', '0')} Kcal",
            "proteina": f"{data.get('proteina', '0')} Prot",
            "ingredients": data.get('ingredients', []),
            "instructions": data.get('instructions', []),
            "image_url": img_url
        }]
    except Exception as e:
        return [{"error": f"Falla en Gemini: {str(e)}"}]

@app.get("/")
async def root():
    return {"mensaje": "Backend estable funcionando"}