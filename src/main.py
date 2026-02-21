import os
import json
from genai import Client
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente moderno de Gemini 2026
client = Client(api_key=os.getenv("GOOGLE_API_KEY"))

@app.get("/search")
async def buscar(query: str = Query(...)):
    prompt = f"Genera una receta para: {query}. Responde solo en JSON con: title, kcal, proteina, ingredients (lista), instructions (lista), img_prompt."
    
    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        txt = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(txt)
        
        # Generación de imagen directa
        img_url = f"https://image.pollinations.ai/prompt/{data['img_prompt'].replace(' ', '%20')}?model=flux&nologo=true"

        # Retornamos exactamente lo que Flutter busca
        return [{
            "title": data.get('title', '').upper(),
            "kcal": f"{data.get('kcal', '---')} Kcal",
            "proteina": f"{data.get('proteina', '---')} Prot",
            "ingredients": data.get('ingredients', []),
            "instructions": data.get('instructions', []),
            "image_url": img_url
        }]
    except Exception as e:
        return [{"title": "ERROR", "instructions": [str(e)], "image_url": ""}]

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)