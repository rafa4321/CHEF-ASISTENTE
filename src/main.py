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
    # Verificación de la API Key en tiempo real
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {"error": "LLAVE_FALTANTE", "detalle": "La variable GROQ_API_KEY no existe en Render"}

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": f"Receta de {query} en JSON"}],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        # Esto nos mostrará el error REAL en el navegador
        return {"error": "FALLO_GROQ", "detalle": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))