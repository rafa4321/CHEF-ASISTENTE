import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/search")
def get_recipe(query: str = Query(...)):
    try:
        # 1. Groq genera la receta fidedigna
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": """Eres un Chef de alta cocina. 
                    Responde SOLO en JSON: {'title': str, 'ingredients': list, 'instructions': str}.
                    IMPORTANTE: No mezcles ingredientes que se sirven por separado."""
                },
                {"role": "user", "content": f"Receta profesional de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        receta = json.loads(completion.choices[0].message.content)
        titulo = receta.get('title', query)

        # 2. LIMPIEZA PARA POLLINATIONS (La clave del éxito)
        # Reemplazamos espacios por guiones y quitamos acentos para evitar el 'robot'
        prompt_limpio = titulo.replace(" ", "-").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
        
        # Construimos la URL de Pollinations forzando estilo fotográfico gourmet
        url_imagen = f"https://image.pollinations.ai/prompt/gourmet-food-photography-of-{prompt_limpio}-plated-luxury-restaurant-style-8k?width=1024&height=1024&nologo=true&enhance=true"
        
        receta['image_url'] = url_imagen

        return [receta] # Enviamos lista para que Flutter no falle

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)