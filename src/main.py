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

@app.get("/search")
async def search_recipe(query: str):
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        return {"title": "Error: Llave no configurada", "ingredients": [], "instructions": []}

    try:
        client = Groq(api_key=api_key)
        
        # System Prompt con filtro de contenido
        prompt = (
            f"Actúa como un Chef de alta cocina. Si el usuario pide algo que NO sea una receta de comida o bebida "
            f"(por ejemplo: '{query}'), responde estrictamente con este JSON: "
            f"{{'title': 'Error: Solo recetas de cocina', 'ingredients': [], 'instructions': []}}. "
            f"Si es comida, genera una receta detallada de {query} en JSON con estos campos: "
            f"title, time, difficulty, ingredients (lista), instructions (lista)."
        )
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"title": "Error de IA", "detalle": str(e), "ingredients": [], "instructions": []}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)