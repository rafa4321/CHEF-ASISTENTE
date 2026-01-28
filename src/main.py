import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Habilitar CORS para que Flutter Web pueda conectarse
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lee la clave desde Render Environment
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

@app.get("/search")
async def search_recipe(query: str = Query(...)):
    prompt = f"""
    Eres un Chef profesional. Genera una receta para: {query}.
    Responde estrictamente en formato JSON con estas claves:
    "title", "ingredients" (como lista), "instructions" (como lista).
    No añadas texto fuera del JSON.
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        # Convertimos a diccionario para que FastAPI lo envíe como UTF-8
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"title": "Error", "ingredients": [], "instructions": [str(e)]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)