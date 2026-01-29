import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Permite que Flutter Web se conecte sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key="TU_API_KEY_AQUI")

@app.get("/search")
async def search_recipe(query: str):
    prompt = f"Crea una receta de {query}. Responde SOLO en JSON con campos: title, time, difficulty, ingredients (lista), instructions (lista)."
    
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        # Retornamos el diccionario directamente para que FastAPI lo envíe como JSON
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"title": "Error", "ingredients": [], "instructions": [], "time": "N/A", "difficulty": "N/A"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))