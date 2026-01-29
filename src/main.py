import os
from fastapi import FastAPI
from groq import Groq
import json

app = FastAPI()
client = Groq(api_key="TU_API_KEY_AQUI")

@app.get("/search")
async def search_recipe(query: str):
    prompt = f"""
    Eres un Chef de alta cocina. Crea una receta para: {query}.
    Responde ÚNICAMENTE en formato JSON con esta estructura exacta:
    {{
      "title": "Nombre del plato",
      "time": "Tiempo estimado",
      "difficulty": "Media/Baja/Alta",
      "ingredients": ["item 1", "item 2"],
      "instructions": ["paso 1", "paso 2"],
      "chef_tip": "Un consejo profesional"
    }}
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        # Convertimos la respuesta de texto a un diccionario real de Python
        recipe_data = json.loads(completion.choices[0].message.content)
        return recipe_data # Enviamos un JSON puro
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)