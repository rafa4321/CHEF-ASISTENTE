import os
import json
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Configuración CORS para que Flutter no tenga bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar cliente de Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/search")
def get_recipe(query: str = Query(...)):
    try:
        # 1. SOLICITUD A GROQ: Forzamos receta fidedigna por componentes
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": """Eres un Chef de alta cocina. 
                    Responde SOLO en JSON con esta estructura: 
                    {
                      'title': str, 
                      'ingredients': list, 
                      'instructions': str
                    }
                    IMPORTANTE: En 'instructions', separa la preparación por componentes (ej: Carne, Arroz, Porotos). 
                    NUNCA indiques mezclar los ingredientes si el plato se sirve por porciones separadas."""
                },
                {"role": "user", "content": f"Receta profesional de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        # Convertimos la respuesta de texto a un objeto JSON de Python
        receta = json.loads(completion.choices[0].message.content)
        titulo_limpio = receta.get('title', query)

        # 2. GENERACIÓN DE LA OBRA DE ARTE (Imagen Gourmet)
        # Usamos un generador dinámico de alta calidad basado en el título de la receta
        # Esto asegura que si buscas 'Pabellón', la imagen sea de un Pabellón Gourmet
        prompt_foto = f"professional_food_photography_of_{titulo_limpio.replace(' ', '_')}_gourmet_plating_studio_lighting_8k_highly_detailed"
        
        # Esta URL genera la imagen en tiempo real para tu App
        receta['image_url'] = f"https://image.pollinations.ai/prompt/{prompt_foto}?width=1024&height=768&nologo=true"

        # 3. ENVIAR TODO A FLUTTER
        return [receta] # Lo enviamos dentro de una lista para que el ListView de Flutter lo lea bien

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)