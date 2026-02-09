import os
import json
import unicodedata
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Configuración CORS para evitar bloqueos en el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def limpiar_texto_para_url(texto):
    """Elimina tildes, eñes y espacios para que Pollinations no falle"""
    # Normaliza para quitar tildes (ej: 'ó' -> 'o')
    texto = "".join(c for c in unicodedata.normalize('NFD', texto)
                  if unicodedata.category(c) != 'Mn')
    # Reemplaza espacios por guiones y quita caracteres especiales
    return texto.replace(" ", "-").replace("ñ", "n").replace("Ñ", "N").lower()

@app.get("/search")
def get_recipe(query: str = Query(...)):
    try:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un Chef experto. Responde SOLO con un JSON: {'title': str, 'ingredients': list, 'instructions': str}."
                },
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        receta = json.loads(completion.choices[0].message.content)
        titulo = receta.get('title', query)

        # Preparamos el prompt para Pollinations
        prompt_limpio = limpiar_texto_para_url(titulo)
        
        # Forzamos estilo de fotografía gastronómica de lujo
        url_base = "https://image.pollinations.ai/prompt/"
        estilo = "gourmet-food-photography-plated-luxury-restaurant-style-8k"
        receta['image_url'] = f"{url_base}{prompt_limpio}-{estilo}?width=1024&height=1024&nologo=true&enhance=true"

        return [receta] # Enviamos lista para compatibilidad con el ListView

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)