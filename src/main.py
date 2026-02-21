import os
import json
from google import genai # Importación correcta para 2026
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializamos el cliente moderno
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

@app.get("/search")
async def buscar_receta(query: str = Query(...)):
    prompt = (
        f"Genera una receta para: {query}. "
        "Responde exclusivamente en formato JSON: "
        '{"title": "Nombre", "kcal": "valor", "proteina": "valor", '
        '"ingredients": ["item1"], "instructions": ["paso1"], '
        '"img_prompt": "comida gourmet de {query}"}'
    )
    
    try:
        # En la librería nueva, el modelo se pone sin el prefijo 'models/'
        response = client.models.generate_content(
            model='gemini-1.5-flash', 
            contents=prompt
        )
        
        # PROTECCIÓN DEFINITIVA: Validamos si hay respuesta antes de usar .text o .strip()
        if not response or not hasattr(response, 'text') or not response.text:
            return [{"error": "Google no generó contenido para esta búsqueda."}]
            
        texto = response.text.strip()
        
        # Limpiamos el texto si Gemini envía markdown
        if "```json" in texto:
            texto = texto.split("```json")[1].split("```")[0].strip()
        elif "```" in texto:
            texto = texto.split("```")[1].split("```")[0].strip()
            
        data = json.loads(texto)
        img_url = f"https://image.pollinations.ai/prompt/{data.get('img_prompt', query).replace(' ', '%20')}?model=flux&nologo=true"

        return [{
            "title": data.get('title', 'Receta').upper(),
            "kcal": f"{data.get('kcal', '0')} Kcal",
            "proteina": f"{data.get('proteina', '0')} Prot",
            "ingredients": data.get('ingredients', []),
            "instructions": data.get('instructions', []),
            "image_url": img_url
        }]
    except Exception as e:
        # Esto atrapará cualquier error y te dirá exactamente qué pasa sin tumbar el servidor
        return [{"error": f"Error en la conexión con Gemini: {str(e)}"}]

@app.get("/")
async def root():
    return {"mensaje": "Backend Chef-Asistente 2.0 operativo"}