import os
import json
import httpx
import base64
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

# --- EL FOTÓGRAFO PROFESIONAL ---
async def generar_imagen_gourmet(titulo_receta):
    # Usamos el modelo más avanzado disponible en tu cuenta
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    
    # Prompt de nivel Michelin
    prompt = f"Professional food photography of {titulo_receta}, plated beautifully, top-down view, natural studio lighting, high resolution, delicious textures, white ceramic plate."
    
    try:
        async with httpx.AsyncClient() as ac:
            response = await ac.post(api_url, headers=headers, json={"inputs": prompt}, timeout=60.0)
            if response.status_code == 200:
                img_data = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/jpeg;base64,{img_data}"
    except Exception as e:
        print(f"Error imagen: {e}")
    
    # Imagen de respaldo de alta calidad (no estatuas)
    return f"https://source.unsplash.com/1600x900/?food,{titulo_receta.replace(' ', '+')}"

@app.get("/search")
async def get_recipe_premium(query: str = Query(...)):
    try:
        system_prompt = """
        Eres un Chef Estrella Michelin. Genera la receta en formato JSON.
        DEBES incluir estos campos exactos para que la App no falle:
        - 'nombre': (String) nombre del plato.
        - 'descripcion': (String) breve y atractiva.
        - 'ingredients': (Lista de Strings).
        - 'steps': (Lista de Strings) Pasos detallados de la preparación.
        - 'nutrition': { 'calories': '...', 'protein': '...', 'carbs': '...', 'fat': '...' }
        """

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Receta profesional para: {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        receta = json.loads(completion.choices[0].message.content)
        
        # Generamos la foto real
        receta['image_url'] = await generar_imagen_gourmet(receta.get('nombre', query))
        
        # Devolvemos lista para compatibilidad con tu Flutter
        return [receta]
        
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)