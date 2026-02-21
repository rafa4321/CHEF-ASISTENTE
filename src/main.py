import os
import json
from google import genai
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuración de CORS para que tu App de Flutter pueda conectar sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializamos el cliente usando la variable de entorno que ya configuraste en Render
# Usamos 'google-genai' (la versión que instalaste satisfactoriamente)
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

@app.get("/search")
async def buscar_receta(query: str = Query(...)):
    prompt = (
        f"Genera una receta de cocina para: {query}. "
        "Responde ESTRICTAMENTE en formato JSON con esta estructura: "
        '{"title": "Nombre", "kcal": "valor", "proteina": "valor", '
        '"ingredients": ["item1", "item2"], "instructions": ["paso1", "paso2"], '
        '"img_prompt": "descripción de imagen para IA"}'
    )
    
    try:
        # Usamos gemini-2.0-flash que es el modelo más actual y compatible
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        
        # Limpieza del texto por si la IA devuelve markdown
        texto_limpio = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(texto_limpio)
        
        # Generador de imagen (Pollinations es gratuito y rápido)
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
        return [{"error": f"Error en la conexión con Gemini: {str(e)}"}]

@app.get("/")
async def root():
    return {"mensaje": "Backend de Chef Asistente funcionando correctamente"}