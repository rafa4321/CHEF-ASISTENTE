import os
import json
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

@app.get("/search")
async def get_recipe_precision(query: str = Query(...)):
    try:
        system_prompt = """
        Eres un Chef Pro. Responde ÚNICAMENTE en JSON.
        REGLAS DE ORO:
        1. 'title': Debe incluir el nombre y al final la nutrición.
        2. 'preparation': Usa este nombre exacto para los pasos. DEBE ser una lista [].
        3. 'ingredients': DEBE ser una lista [].
        """

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Receta para {query}. Dame título con calorías y lista de preparación."}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        raw_data = json.loads(completion.choices[0].message.content)
        
        # EXTREMO DERECHO: Creamos un título con espacios para empujar la nutrición
        nombre = raw_data.get("title", query).split('|')[0].strip()
        nutricion = "Cal: 450 | Prot: 30g" # Simplificado para la prueba
        # Usamos muchos espacios para intentar forzar el desplazamiento a la derecha en la franja
        titulo_formateado = f"{nombre}                                           {nutricion}"

        # DUPLICAMOS las llaves para asegurar que Flutter encuentre la información
        # Si tu app busca 'steps', 'preparation' o 'instrucciones', aquí las encontrará todas
        pasos = raw_data.get("preparation", raw_data.get("steps", []))
        if isinstance(pasos, str): pasos = [pasos]

        resultado = {
            "title": titulo_formateado,
            "description": raw_data.get("description", ""),
            "ingredients": raw_data.get("ingredients", []),
            "preparation": pasos,
            "steps": pasos, # Duplicado por seguridad
            "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"
        }
        
        return [resultado]
    except Exception as e:
        return [{"error": str(e)}]