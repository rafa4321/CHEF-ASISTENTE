import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Configuración necesaria para conectar Flutter Web con Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REEMPLAZA ESTO CON TU CLAVE DE API DE GROQ
client = Groq(api_key="TU_CLAVE_AQUI")

@app.get("/search")
async def search_recipe(query: str = Query(...)):
    # Forzamos a la IA a responder en un JSON estructurado
    prompt = f"""
    Eres un Chef experto. Genera una receta detallada para: {query}.
    Responde ÚNICAMENTE en formato JSON con esta estructura exacta:
    {{
      "title": "Nombre de la receta",
      "ingredients": ["ingrediente 1", "ingrediente 2"],
      "instructions": ["paso 1", "paso 2"],
      "description": "Breve descripción."
    }}
    Si no es comida, el título debe decir 'Solo soy un Chef'.
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        
        # Cargamos el contenido como diccionario. 
        # FastAPI enviará esto automáticamente como UTF-8 para evitar errores 'ascii'
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"title": "Error de conexión", "ingredients": [], "instructions": [str(e)]}

if __name__ == "__main__":
    import uvicorn
    # Render usa el puerto 10000 por defecto
    uvicorn.run(app, host="0.0.0.0", port=10000)