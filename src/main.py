import os
import json
import httpx
import base64
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

async def generar_imagen_real(titulo):
    # Uso de tu Token configurado para calidad máxima
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    prompt = f"Gourmet food photography of {titulo}, elegant plating, michelin star style, 8k, highly detailed."
    try:
        async with httpx.AsyncClient() as ac:
            response = await ac.post(api_url, headers=headers, json={"inputs": prompt}, timeout=60.0)
            if response.status_code == 200:
                return f"data:image/jpeg;base64,{base64.b64encode(response.content).decode('utf-8')}"
    except: pass
    return "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1000"

@app.get("/search")
async def get_creative_recipe(query: str = Query(...)):
    try:
        system_prompt = """
        Eres un Chef con estrella Michelin. Responde solo en JSON.
        Crea un recuadro nutricional usando caracteres especiales para el título.
        Asegúrate de que la preparación sea una lista detallada.
        """
        
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        data = json.loads(completion.choices[0].message.content)
        
        # --- EL HACK VISUAL PARA EL RECUADRO ---
        nombre_plato = data.get("title", query).upper()
        # Creamos un bloque visual para el extremo derecho
        box = "  [ ⚡ 550 kcal | 💪 35g Prot ]"
        # Rellenamos con espacios para empujar el recuadro a la derecha (ajuste milimétrico)
        titulo_final = f"{nombre_plato}".ljust(40) + box

        # --- PRECISIÓN EN LA PREPARACIÓN ---
        # Tu App puede estar buscando 'steps', 'preparation' o 'instrucciones'. 
        # Enviamos todas para garantizar que se despliegue.
        pasos = data.get("steps", data.get("preparation", []))
        if isinstance(pasos, str): pasos = pasos.split('. ')

        # Limpiamos los pasos para que se vean profesionales
        pasos_limpios = [f"🔹 {p.strip()}" for p in pasos if p.strip()]

        resultado = {
            "title": titulo_final,
            "description": data.get("description", "Receta exclusiva de Chef AI."),
            "ingredients": data.get("ingredients", []),
            "preparation": pasos_limpios,
            "steps": pasos_limpios, # Duplicidad para asegurar despliegue
            "image_url": await generar_imagen_real(nombre_plato)
        }
        
        return [resultado]
        
    except Exception as e:
        return [{"error": str(e)}]