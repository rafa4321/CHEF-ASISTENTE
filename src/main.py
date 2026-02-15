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
async def get_recipe_fixed(query: str = Query(...)):
    try:
        system_prompt = """
        Eres un Chef Pro. Responde SOLO en JSON.
        ESTRUCTURA:
        {
          "nombre": "TITULO",
          "kcal": "800 kcal",
          "prot": "50g Prot",
          "ingredientes": ["item 1", "item 2"],
          "pasos": ["1. Paso uno", "2. Paso dos"]
        }
        IMPORTANTE: 'pasos' debe ser una LISTA de frases cortas, NO un párrafo.
        """

        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        data = json.loads(completion.choices[0].message.content)
        
        # --- DISEÑO DEL TÍTULO (Recuadro a la derecha) ---
        # Usamos tabulaciones y espacios para empujar la info nutricional
        nombre = data.get("nombre", query).upper()
        nutricion = f"⚡ {data.get('kcal', '--')}  |  💪 {data.get('prot', '--')}"
        # El título final llevará el nombre y la nutrición separada
        titulo_final = f"{nombre}                                         {nutricion}"

        # --- CORRECCIÓN DE LA PREPARACIÓN ---
        # Forzamos que 'pasos' sea una lista real para que Flutter la pinte
        raw_pasos = data.get("pasos", [])
        if isinstance(raw_pasos, str):
            # Si la IA manda texto, lo partimos por los puntos
            pasos_finales = [p.strip() for p in raw_pasos.split('.') if len(p) > 5]
        else:
            pasos_finales = raw_pasos

        # Enviamos los nombres de variables que Flutter espera (redundancia total)
        resultado = {
            "title": titulo_final,
            "ingredients": data.get("ingredientes", []),
            "preparation": pasos_finales, # Etiqueta principal
            "steps": pasos_finales,       # Etiqueta secundaria
            "description": f"Receta de {nombre}",
            "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"
        }
        
        return [resultado]
    except Exception as e:
        return [{"title": "ERROR", "preparation": [str(e)], "ingredients": []}]