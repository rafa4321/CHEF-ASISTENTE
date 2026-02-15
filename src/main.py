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
async def buscar_receta_perfecta(query: str = Query(...)):
    try:
        # Prompt de ingeniería de precisión: Forzamos idioma y estructura de lista
        system_prompt = """
        Eres un Chef Estrella Michelin. 
        REGLA 1: Responde SIEMPRE en ESPAÑOL.
        REGLA 2: La preparación NO puede ser un solo bloque de texto. 
        REGLA 3: Debes separar cada instrucción en un elemento distinto de la lista.
        FORMATO JSON REQUERIDO:
        {
          "nombre": "TITULO",
          "kcal": "500 kcal",
          "prote": "30g Prot",
          "ingredientes": ["item 1", "item 2"],
          "pasos": ["1. Primer paso", "2. Segundo paso", "3. Tercer paso"]
        }
        """

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Receta para: {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        data = json.loads(completion.choices[0].message.content)
        
        # --- Formateo de Título para tu App ---
        nombre_plato = data.get("nombre", query).upper()
        info_nutri = f"⚡ {data.get('kcal', '---')}  |  💪 {data.get('prote', '---')}"
        titulo_final = f"{nombre_plato}         {info_nutri}"

        # --- Extracción Segura de Listas ---
        # Si la IA falla, enviamos una lista con un mensaje para que Flutter no se rompa
        lista_ingredientes = data.get("ingredientes", ["No se cargaron ingredientes"])
        lista_pasos = data.get("pasos", ["No se cargó la preparación"])

        # --- El Puente de Datos (Lo que Flutter recibe) ---
        return [{
            "title": titulo_final,
            "ingredients": lista_ingredientes,
            "preparation": lista_pasos, # Flutter leerá esta lista de strings individuales
            "steps": lista_pasos,       # Duplicado por si tu código busca 'steps'
            "description": f"Receta profesional de {nombre_plato}",
            "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"
        }]
    except Exception as e:
        # Si algo falla, devolvemos una estructura de lista para evitar la pantalla roja
        return [{"title": "ERROR", "ingredients": [], "preparation": [str(e)]}]