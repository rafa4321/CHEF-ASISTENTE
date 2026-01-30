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
    client = Groq(api_key=api_key)
    
    # EL FILTRO MAESTRO: Bloqueo explícito de no-comida
    prompt = (
        f"Eres un Chef. Si '{query}' no es un alimento o bebida para humanos, "
        f"responde estrictamente: {{\"title\": \"ERROR: SOLO COMIDA\", \"ingredients\": [], \"instructions\": []}}. "
        f"Si es comida, genera la receta de {query} en JSON con title, ingredients, instructions, time y difficulty."
    )
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(completion.choices[0].message.content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))