import os
import json
import re
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def formatear_a_lista(texto_o_lista):
    """Asegura que la preparación sea una lista de strings para Flutter."""
    if isinstance(texto_o_lista, list):
        return [str(i).strip() for i in texto_o_lista if i]
    if isinstance(texto_o_lista, str):
        # Divide por números (1., 2.) o puntos seguidos de mayúscula
        pasos = re.split(r'\d+\.\s*|\.\s*(?=[A-Z])', texto_o_lista)
        return [p.strip() for p in pasos if len(p.strip()) > 5]
    return []

@app.get("/search")
async def buscar_receta(query: str = Query(...)):
    try:
        prompt_estricto = f"""
        Genera una receta para '{query}' EXCLUSIVAMENTE en ESPAÑOL.
        Responde SOLO con un objeto JSON siguiendo este esquema exacto:
        {{
          "titulo": "NOMBRE DEL PLATO",
          "kcal": "VALOR Kcal",
          "prote": "VALOR Prot",
          "ingredientes": ["item 1", "item 2"],
          "preparacion": ["Paso 1", "Paso 2"]
        }}
        """

        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": "Eres un chef experto que solo habla español y responde en JSON."},
                      {"role": "user", "content": prompt_estricto}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        res_ai = json.loads(completion.choices[0].message.content)
        
        # Procesamos los datos para que coincidan con los campos que tu App ya lee
        ingredientes = formatear_a_lista(res_ai.get("ingredientes", []))
        pasos = formatear_a_lista(res_ai.get("preparacion", res_ai.get("pasos", [])))

        # Construcción del título con estética de caja (como en tus fotos)
        kcal = res_ai.get("kcal", "---")
        prote = res_ai.get("prote", "---")
        titulo_display = f"{res_ai.get('titulo', query).upper()}    | {kcal} | {prote} |"

        # Retornamos exactamente lo que tu App espera recibir
        return [{
            "title": titulo_display,
            "ingredients": ingredientes,
            "preparation": pasos,  # Esta es la llave crítica para el despliegue
            "description": f"Receta profesional de {query}",
            "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"
        }]
    except Exception as e:
        return [{"title": "ERROR", "preparation": [f"Error: {str(e)}"], "ingredients": []}]