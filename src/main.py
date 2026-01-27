import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# REEMPLAZA ESTO CON TU CLAVE GSK_...
client = Groq(api_key="TU_API_KEY_REAL_AQUI")

@app.get("/search")
async def search_recipe(query: str = Query(...)):
    prompt = f"Eres un chef. Genera una receta para {query} en JSON con: title, ingredients (lista), instructions (lista)."
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        # Convertimos a diccionario. FastAPI maneja el UTF-8 correctamente
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"title": "Error", "ingredients": [], "instructions": [str(e)]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)