import os
import json
import re
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

def procesar_pasos(texto_o_lista):
    """Convierte cualquier respuesta de pasos en una lista real para Flutter."""
    if isinstance(texto_o_lista, list):
        # Si ya es lista pero tiene un solo elemento largo, lo dividimos
        if len(texto_o_lista) == 1:
            texto = texto_o_lista[0]
        else:
            return texto_o_lista
    else:
        texto = str(texto_o_lista)
    
    # Dividimos por números (1., 2., etc) o por puntos seguidos de mayúsculas
    pasos = re.split(r'\d+\.\s*|\.\s*(?=[A-Z])', texto)
    return [p.strip() for p in pasos if len(p.strip()) > 5]

@app.get("/search")
async def get_recipe_perfect(query: str = Query(...)):
    try:
        system_prompt = """
        Responde SOLO en JSON. 
        Formato: {"n": "NOMBRE", "k": "500", "p": "30g", "i": ["ing1"], "s": ["paso1", "paso2"]}
        """
        
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        data = json.loads(completion.choices[0].message.content)
        
        # 1. DISEÑO DE TÍTULO SIN CORCHETES (Limpio a la derecha)
        nombre_mayus = str(data.get("n", query)).upper()
        nutricion = f"⚡ {data.get('k', '--')} kcal   |   💪 {data.get('p', '--')} Prot"
        # Usamos padding para empujar la info a la derecha
        titulo_final = f"{nombre_mayus:<30} {nutricion:>30}"

        # 2. PROCESAMIENTO DE PREPARACIÓN (Inmediato y Real)
        lista_pasos = procesar_pasos(data.get("s", []))

        # 3. RESULTADO FINAL PARA FLUTTER
        return [{
            "title": titulo_final,
            "ingredients": data.get("i", []),
            "preparation": lista_pasos, # Flutter leerá esta lista de strings individuales
            "steps": lista_pasos,       # Duplicamos por seguridad de mapeo
            "description": f"Chef AI Premium: {nombre_mayus}",
            "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"
        }]
    except Exception as e:
        return [{"title": "ERROR SISTEMA", "preparation": [str(e)], "ingredients": []}]