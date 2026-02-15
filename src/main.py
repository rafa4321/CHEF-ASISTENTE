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
async def get_recipe_final(query: str = Query(...)):
    try:
        # Prompt ultra-estricto para evitar listas vacías
        system_prompt = """
        Eres un Chef Estrella Michelin. Genera una receta detallada en JSON.
        REGLAS DE ORO:
        1. 'title': Nombre del plato en MAYÚSCULAS.
        2. 'nutri': Texto con este formato: ⚡ 550 kcal  |  💪 35g Prot
        3. 'ingredients': DEBE ser una lista de strings. No puede estar vacía.
        4. 'steps': DEBE ser una lista de pasos numerados. No puede estar vacía.
        """

        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        data = json.loads(completion.choices[0].message.content)
        
        # Extracción y limpieza de datos
        nombre = data.get("title", query).upper()
        info_nutri = data.get("nutri", "⚡ -- kcal | 💪 --g Prot")
        
        # Hack para el alineado a la derecha sin corchetes
        # Usamos puntos invisibles o espacios para empujar el texto
        titulo_final = f"{nombre}                                     {info_nutri}"

        ingredientes = data.get("ingredients", ["Error: No se cargaron ingredientes"])
        pasos = data.get("steps", ["Error: No se cargó la preparación"])

        # Retornamos el objeto con TODAS las etiquetas posibles que tu App pueda buscar
        resultado = {
            "title": titulo_final,
            "description": data.get("description", ""),
            "ingredients": ingredientes,
            "preparation": pasos, # Para el widget de preparación
            "steps": pasos,       # Por si acaso busca 'steps'
            "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"
        }
        
        return [resultado]
    except Exception as e:
        return [{"title": "ERROR DE CONEXIÓN", "ingredients": [], "preparation": [str(e)]}]