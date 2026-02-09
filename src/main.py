import os
import json
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def obtener_imagen_segmind(prompt_comida):
    url = "https://api.segmind.com/v1/sdxl1.0-txt2img"
    # Usamos un prompt optimizado para realismo
    payload = {
        "prompt": f"Professional food photography of {prompt_comida}, 8k, highly detailed, appetizing, studio lighting",
        "samples": 1,
        "scheduler": "dpmpp_2m",
        "num_inference_steps": 25,
        "guidance_scale": 7.5,
        "img_width": 1024,
        "img_height": 768,
        "base64": False # Esto nos da la URL directamente
    }
    headers = {'x-api-key': os.getenv("SEGMIND_API_KEY")}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get('url')
        return None
    except:
        return None

@app.get("/search")
def get_recipe(query: str = Query(...)):
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Chef experto. Responde SOLO JSON: {'title': str, 'ingredients': list, 'instructions': str}."},
                {"role": "user", "content": f"Receta de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        receta = json.loads(completion.choices[0].message.content)
        # Llamada al nuevo canal: Segmind
        receta['image_url'] = obtener_imagen_segmind(receta.get('title', query))
        return [receta]
    except Exception as e:
        return {"error": str(e)}