import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Configuración de CORS para evitar bloqueos en el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REEMPLAZA CON TU CLAVE REAL DE GROQ
client = Groq(api_key="TU_CLAVE_DE_GROQ_AQUÍ")

@app.get("/search")
async def search_recipe(query: str = Query(...)):
    # Prompt diseñado para obtener JSON puro y real
    prompt = f"""
    Eres un Chef profesional. Genera una receta detallada y real para: {query}.
    Responde estrictamente en formato JSON con esta estructura:
    {{
      "title": "Nombre de la receta",
      "ingredients": ["1 unidad de algo", "500g de otro"],
      "instructions": ["Paso 1...", "Paso 2..."],
      "description": "Breve reseña."
    }}
    Si el tema no es cocina, indica que solo eres un Chef.
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        # Convertimos la respuesta en un diccionario de Python
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"title": "Error", "ingredients": [], "instructions": [str(e)]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)