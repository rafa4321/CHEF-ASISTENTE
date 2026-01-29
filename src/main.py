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
    Eres un Chef. Genera una receta para: {query}.
    Responde estrictamente en JSON con este formato:
    {{
      "title": "Nombre",
      "time": "Tiempo",
      "difficulty": "Nivel",
      "ingredients": ["item 1", "item 2"],
      "instructions": ["paso 1", "paso 2"]
    }}
    """
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        # Validamos los datos antes de enviarlos a Flutter
        raw_data = json.loads(completion.choices[0].message.content)
        
        return {
            "title": str(raw_data.get("title", "Receta")),
            "time": str(raw_data.get("time", "N/A")),
            "difficulty": str(raw_data.get("difficulty", "N/A")),
            "ingredients": list(raw_data.get("ingredients", [])),
            "instructions": list(raw_data.get("instructions", []))
        }
    except Exception as e:
        return {"title": "Error de conexión", "ingredients": [], "instructions": [], "time": "N/A", "difficulty": "N/A"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))