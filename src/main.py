import os
import json
import re
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def limpiar_y_listar(datos):
    """Convierte cualquier basura en una lista limpia de strings."""
    if isinstance(datos, list): return [str(i).strip() for i in datos if i]
    if isinstance(datos, str):
        # Si es un texto largo, lo dividimos por puntos o números
        pasos = re.split(r'\d+\.\s*|\.\s*(?=[A-Z])', datos)
        return [p.strip() for p in pasos if len(p.strip()) > 5]
    return []

@app.get("/search")
async def buscar_receta(query: str = Query(...)):
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": "Chef JSON: title, calories, protein, ingredients (list), steps (list)."},
                      {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        res_ai = json.loads(completion.choices[0].message.content)
        
        # 1. DISEÑO DE TÍTULO (Nombre + 'Caja' Nutricional a la derecha)
        # Usamos caracteres de bloque para simular el rectángulo que pides
        nombre = str(res_ai.get("title", query)).upper()
        kcal = res_ai.get("calories", "---")
        prot = res_ai.get("protein", "---")
        
        # Este formato empuja la info a la derecha si tu App usa una fuente monoespaciada o un contenedor ancho
        caja_nutri = f" █ {kcal} Kcal | {prot} Prot █ "
        titulo_final = f"{nombre:<25} {caja_nutri:>25}"

        # 2. PROCESAMIENTO RIGUROSO DE LISTAS
        # Usamos nombres redundantes porque no sabemos cuál espera tu código Dart
        ingredientes = limpiar_y_listar(res_ai.get("ingredients", []))
        pasos = limpiar_y_listar(res_ai.get("steps", res_ai.get("preparation", [])))

        # 3. EL PUENTE (El JSON que no falla)
        return [{
            "title": titulo_final,
            "ingredients": ingredientes,
            "preparation": pasos,  # Llave que suele usar Flutter
            "steps": pasos,        # Llave alternativa
            "description": "Receta optimizada para el sistema.",
            "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"
        }]
    except Exception as e:
        return [{"title": "ERROR DE MAPEO", "preparation": [str(e)], "ingredients": []}]