import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key="TU_API_KEY_AQUI")

@app.get("/search")
async def search_recipe(query: str):
    prompt = f"""
    Eres un Chef estrella. Crea una receta detallada para: {query}.
    Responde ÚNICAMENTE en formato JSON con estos campos:
    "title", "time", "difficulty", "ingredients" (lista), "instructions" (lista), "chef_tip".
    """
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        # Convertimos la respuesta en un diccionario real de Python
        data = json.loads(completion.choices[0].message.content)
        
        # Estructura de salida garantizada (evita nulos en el cliente)
        return {
            "title": data.get("title", "Receta"),
            "time": data.get("time", "N/A"),
            "difficulty": data.get("difficulty", "N/A"),
            "ingredients": data.get("ingredients", []),
            "instructions": data.get("instructions", []),
            "chef_tip": data.get("chef_tip", "")
        }
    except Exception as e:
        return {"error": str(e), "ingredients": [], "instructions": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))