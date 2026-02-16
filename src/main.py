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

async def generar_imagen_ia(descripcion):
    """Genera imagen Base64 usando Hugging Face"""
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    try:
        async with httpx.AsyncClient() as ac:
            # Prompt simplificado para evitar errores
            response = await ac.post(api_url, headers=headers, json={"inputs": f"Gourmet plating of {descripcion}, professional food photography, 8k"}, timeout=40.0)
            if response.status_code == 200:
                return f"data:image/jpeg;base64,{base64.b64encode(response.content).decode('utf-8')}"
    except: pass
    return "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=1000"

@app.get("/search")
async def buscar(query: str = Query(...)):
    try:
        # Prompt ultra-claro para evitar el Error 400
        system_prompt = "Eres un Chef. Responde SOLO en JSON con esta estructura exacta: {'title': '...', 'kcal': '...', 'prot': '...', 'ing': ['lista'], 'ins': ['paso1', 'paso2']}"
        
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        data = json.loads(completion.choices[0].message.content)
        foto = await generar_imagen_ia(data.get("title", query))

        return [{
            "title": data.get("title", query).upper(),
            "kcal": data.get("kcal", "500"),
            "proteina": data.get("prot", "20g"),
            "ingredients": data.get("ing", []),
            "instructions": data.get("ins", []), # Lista de pasos
            "image_url": foto
        }]
    except Exception as e:
        return [{"title": "ERROR", "instructions": [str(e)], "ingredients": []}]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))