import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/search")
async def buscar_receta_definitiva(query: str = Query(...)):
    try:
        # Prompt ultra-específico para tu código Flutter
        system_prompt = """
        Eres un Chef Pro. Responde solo en JSON y en ESPAÑOL.
        Usa estos campos EXACTOS:
        {
          "title": "NOMBRE DEL PLATO | ⚡ 500 kcal | 💪 30g Prot",
          "ingredients": ["ingrediente 1", "ingrediente 2"],
          "instructions": "1. Paso uno\\n2. Paso dos\\n3. Paso tres"
        }
        Nota: 'instructions' debe ser un solo texto con saltos de línea (\\n).
        """

        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        data = json.loads(completion.choices[0].message.content)
        
        # Extraemos los datos del JSON de la IA
        titulo = data.get("title", query).upper()
        ingredientes = data.get("ingredients", [])
        # Forzamos que 'instructions' sea un string para tu widget Text(r['instructions'])
        instrucciones = data.get("instructions", "No se cargó la preparación.")
        
        if isinstance(instrucciones, list):
            instrucciones = "\n".join([f"• {i}" for i in instrucciones])

        # EL PUENTE FINAL: Retornamos exactamente lo que SearchScreen espera
        return [{
            "title": titulo,
            "ingredients": ingredientes,
            "instructions": instrucciones,  # <--- ESTA ES LA PALABRA CLAVE
            "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000",
            "description": f"Receta de {titulo}"
        }]
    except Exception as e:
        return [{"title": "ERROR", "ingredients": [], "instructions": str(e)}]