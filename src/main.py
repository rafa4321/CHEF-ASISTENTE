import os, base64, requests, json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Esto permite que tu aplicación Flutter (Frontend) hable con Render (Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de Groq para la receta
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/search")
def get_recipe(query: str = Query(...)):
    try:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un Chef. Responde SOLO con un JSON: {'title': str, 'ingredients': list, 'instructions': str}."
                },
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

# Este endpoint ahora es opcional porque Flutter cargará la imagen directo,
# pero lo dejamos para que el servidor no dé error si Flutter lo llama.
@app.get("/generate-image")
def generate_image(prompt: str = Query(...)):
    return {"status": "ok", "message": "Cargando desde el frontend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)