import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/search")
async def buscar_receta(query: str = Query(...)):
    try:
        # CONTRATO INVIOLABLE: Definimos el esquema exacto que la IA DEBE seguir
        esquema_instrucciones = """
        Responde exclusivamente en ESPAÑOL y en formato JSON profesional.
        Estructura:
        {
          "titulo_plato": "Nombre en Mayúsculas",
          "calorias": "850 kcal",
          "proteinas": "60g",
          "lista_ingredientes": ["elemento 1", "elemento 2"],
          "lista_pasos": ["1. Paso uno", "2. Paso dos"]
        }
        IMPORTANTE: 'lista_pasos' debe ser un ARRAY de frases cortas, no un párrafo largo.
        """

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": esquema_instrucciones},
                {"role": "user", "content": f"Genera la receta de: {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)
        
        # --- REINVENCIÓN DEL TÍTULO (Sin corchetes, estética de bloque) ---
        nombre = res.get("titulo_plato", query).upper()
        nutricion = f"⚡ {res.get('calorias', '---')}  |  💪 {res.get('proteinas', '---')}"
        # Concatenamos con espacios para que Flutter lo pinte en la cabecera
        titulo_app = f"{nombre}           {nutricion}"

        # --- NORMALIZACIÓN PARA FLUTTER ---
        # Tu App de Flutter parece buscar 'ingredients' y 'preparation'
        return [{
            "title": titulo_app,
            "ingredients": res.get("lista_ingredientes", []),
            "preparation": res.get("lista_pasos", []), # Aquí está la clave del despliegue
            "steps": res.get("lista_pasos", []),       # Doble check por si acaso
            "description": f"Receta optimizada para {nombre}",
            "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"
        }]

    except Exception as e:
        return [{"title": "ERROR DE CONEXIÓN", "preparation": ["Reintenta la búsqueda"], "ingredients": []}]