import os
import json
import unicodedata
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

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def limpiar_simple(texto):
    # Elimina acentos y deja solo letras y guiones
    texto = "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto.replace(" ", "-").lower()

@app.get("/search")
def get_recipe(query: str = Query(...)):
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Chef experto. Responde SOLO JSON: {'title': str, 'ingredients': list, 'instructions': str}. No uses caracteres especiales."},
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        receta = json.loads(completion.choices[0].message.content)
        # URL ultra-simple para evitar el error 403
        prompt = limpiar_simple(receta.get('title', query))
        receta['image_url'] = f"https://image.pollinations.ai/prompt/food-photo-{prompt}?width=1024&height=768&nologo=true"

        return [receta]
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)