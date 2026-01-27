import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ASEGÚRATE DE USAR UNA CLAVE VÁLIDA
client = Groq(api_key="TU_CLAVE_DE_GROQ_AQUÍ")

@app.get("/search")
async def search_recipe(query: str = Query(...)):
    prompt = f"""
    Eres un Chef. Genera una receta para: {query}.
    Responde estrictamente en JSON:
    {{
      "title": "Nombre",
      "ingredients": ["1 unidad", "2 tazas"],
      "instructions": ["Paso 1", "Paso 2"]
    }}
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        # Convertimos a diccionario. FastAPI enviará esto como UTF-8 automáticamente
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"title": "Error", "ingredients": [], "instructions": [str(e)]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)