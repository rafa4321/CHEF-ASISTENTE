import os
import json
import httpx
import base64
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def generar_foto_ia(nombre_plato, ingredientes_clave=""):
    # URL actualizada al Router de Hugging Face
    url_hf = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {
        "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
        "Content-Type": "application/json",
        "x-wait-for-model": "true" # Obliga a esperar si el modelo está cargando
    }
    
    # Mejoramos el prompt basándonos en el nombre y los ingredientes para que sea REALISTA
    # Si es Asado Negro, la IA sabrá que es carne oscura, no una ensalada.
    prompt = f"Gourmet food photography of {nombre_plato}, professional plating, high resolution, 4k. Ingredients: {ingredientes_clave}. Cinematic lighting, delicious texture."

    try:
        async with httpx.AsyncClient() as ac:
            response = await ac.post(
                url_hf, 
                headers=headers, 
                json={"inputs": prompt}, 
                timeout=60.0
            )
            
            if response.status_code == 200:
                img_b64 = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/jpeg;base64,{img_b64}"
            else:
                # Si falla, imprimimos el error exacto en los logs de Render
                print(f"ERROR HF ({response.status_code}): {response.text}")
                return "" # DEVOLVEMOS VACÍO PARA NO MOSTRAR FOTOS FALSAS
    except Exception as e:
        print(f"EXCEPCIÓN IA: {e}")
        return ""

@app.get("/search")
async def buscar(query: str = Query(...)):
    try:
        # Pedimos a Llama que nos de el JSON y una breve descripción física del plato
        system_prompt = "Eres un Chef. Responde en JSON: {title, kcal, prot, ing:[], ins:[], description: 'breve descripcion visual'}"
        
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        res = json.loads(completion.choices[0].message.content)
        
        # Usamos el título Y los primeros 3 ingredientes para que la foto sea exacta
        tags_visuales = ", ".join(res.get("ing", [])[:3])
        foto_data = await generar_foto_ia(res.get("title", query), tags_visuales)

        return [{
            "title": res.get("title", "RECETA").upper(),
            "kcal": f"{res.get('kcal', '---')} Kcal",
            "proteina": f"{res.get('prot', '---')} Prot",
            "ingredients": res.get("ing", []),
            "instructions": res.get("ins", []),
            "image_url": foto_data # Si está vacío, Flutter mostrará un icono de comida
        }]
    except Exception as e:
        return [{"title": "ERROR", "instructions": [str(e)], "image_url": ""}]