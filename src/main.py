import os
import json
import httpx
import base64
import asyncio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Configuración de CORS para permitir la conexión con Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialización de Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def generar_foto_ia(nombre_plato: str):
    """
    Se comunica con Hugging Face para generar una imagen única.
    Retorna un string Base64 que Flutter puede renderizar.
    """
    url_hf = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    
    try:
        async with httpx.AsyncClient() as ac:
            payload = {
                "inputs": f"Professional gourmet food photography of {nombre_plato}, 8k resolution, highly detailed, appetizing, cinematic lighting",
                "parameters": {"wait_for_model": True} # Obliga a esperar si el modelo está cargando
            }
            # Tiempo de espera extendido a 60s para asegurar la generación
            response = await ac.post(url_hf, headers=headers, json=payload, timeout=60.0)
            
            if response.status_code == 200:
                img_b64 = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/jpeg;base64,{img_b64}"
            else:
                print(f"Error HF: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Excepción en generación de imagen: {e}")
    
    # Imagen genérica de respaldo si la IA falla o agota la cuota
    return "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"

@app.get("/search")
async def buscar(query: str = Query(...)):
    try:
        # Prompt técnico para asegurar precisión en ingredientes y pasos
        system_prompt = """
        Eres un Chef Profesional. Responde SIEMPRE en formato JSON estricto.
        Si la consulta NO es culinaria (ej. 'retrovisor'), devuelve: {"valido": false, "error": "Solo respondo dudas culinarias."}
        
        Si es culinaria, devuelve:
        {
            "valido": true,
            "title": "NOMBRE DEL PLATO",
            "kcal": "Valor",
            "prot": "Gramos",
            "ing": ["Lista de ingredientes"],
            "ins": ["Pasos de preparación numerados"]
        }
        """
        
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)

        # Si el filtro ético o temático se activa
        if not res.get("valido", True):
            return [{
                "title": "AVISO",
                "instructions": [res.get("error")],
                "ingredients": [],
                "image_url": "https://images.unsplash.com/photo-1594312915251-48db9280c8f1?w=500"
            }]

        # PROCESO CRÍTICO: Generar la imagen ANTES de enviar la respuesta
        # Usamos el título generado por la IA para mayor precisión visual
        nombre_para_foto = res.get("title", query)
        foto_base64 = await generar_foto_ia(nombre_para_foto)

        # Respuesta final estructurada para Flutter
        return [{
            "title": res.get("title", "").upper(),
            "kcal": f"{res.get('kcal')} Kcal",
            "proteina": f"{res.get('prot')} Prot",
            "ingredients": res.get("ing", []),
            "instructions": res.get("ins", []),
            "image_url": foto_base64
        }]
        
    except Exception as e:
        return [{"title": "ERROR DE SISTEMA", "instructions": [str(e)], "ingredients": []}]

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)