import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/search")
async def buscar_receta_detallada(query: str = Query(...)):
    try:
        # Prompt de ALTA PRECISIÓN para evitar ambigüedades
        system_prompt = """
        Eres un Chef Profesional de alto nivel. Responde SIEMPRE en ESPAÑOL y en formato JSON.
        
        REGLAS DE ORO:
        1. INGREDIENTES: Deben incluir cantidades exactas (ej: "500g de carne", "2 tazas de arroz", "1 pizca de sal"). No acepto ingredientes sin medida.
        2. PREPARACIÓN: Debe ser detallada y técnica. Explica tiempos de cocción, tipos de fuego y texturas esperadas.
        3. FORMATO: Usa exactamente estos campos:
        {
          "title": "NOMBRE DEL PLATO | ⚡ 850 kcal | 💪 45g Prot",
          "ingredients": ["Cantidad + Ingrediente 1", "Cantidad + Ingrediente 2"],
          "instructions": "1. [Detalle técnico del paso 1]\\n2. [Detalle técnico del paso 2]"
        }
        """

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Genera una receta profesional y detallada para: {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        data = json.loads(completion.choices[0].message.content)
        
        # Aseguramos que las instrucciones sean un solo bloque de texto con saltos de línea
        instrucciones = data.get("instructions", "")
        if isinstance(instrucciones, list):
            instrucciones = "\n".join(instrucciones)

        return [{
            "title": data.get("title", query).upper(),
            "ingredients": data.get("ingredients", []),
            "instructions": instrucciones,
            "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000",
            "description": f"Receta detallada de {query}"
        }]
    except Exception as e:
        return [{"title": "ERROR", "ingredients": [], "instructions": str(e)}]