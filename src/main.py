import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Configuración para evitar errores de conexión en la web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# REEMPLAZA CON TU CLAVE REAL DE GROQ
client = Groq(api_key="TU_CLAVE_AQUI")

@app.get("/search")
async def search_recipe(query: str = Query(...)):
    prompt = f"Genera una receta de {query} en JSON con: title, ingredients (lista), instructions (lista)."
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        # FastAPI envía esto como UTF-8 automáticamente, corrigiendo el error 'ascii'
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"title": "Error", "ingredients": [], "instructions": [str(e)]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)