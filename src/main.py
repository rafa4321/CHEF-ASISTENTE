import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from groq import Groq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Se inicializa el cliente con la variable de entorno de Render
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.get("/search")
async def search_recipe(query: str = Query(...)):
    prompt = f"Genera una receta de {query} en JSON. Usa exclusivamente estas llaves: 'title', 'ingredients' (lista), 'instructions' (lista). Responde solo el JSON, sin texto extra."
    
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile", # Modelo actualizado y soportado
            response_format={"type": "json_object"}
        )
        
        contenido = json.loads(completion.choices[0].message.content)
        
        # JSONResponse garantiza que se envíe como UTF-8
        return JSONResponse(content=contenido, media_type="application/json; charset=utf-8")
        
    except Exception as e:
        return JSONResponse(
            content={"title": "Error", "ingredients": [], "instructions": [str(e)]},
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)