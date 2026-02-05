import os, base64, requests, json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

app = FastAPI()

# Configuración de CORS para permitir que Flutter Web se comunique sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/search")
def get_recipe(query: str = Query(...)):
    try:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un Chef experto. Responde ÚNICAMENTE con un objeto JSON plano que contenga: 'title' (string), 'ingredients' (lista de strings) e 'instructions' (string). No agregues texto fuera del JSON."
                },
                {"role": "user", "content": f"Receta detallada de {query}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"error": f"Error en Groq: {str(e)}"}

@app.get("/generate-image")
def generate_image(prompt: str = Query(...)):
    try:
        # Usamos Pollinations con parámetros de limpieza (nologo=true)
        # Esto evita que se generen formatos extraños que rompan el Codec de Flutter
        clean_prompt = prompt.replace(" ", "%20")
        url = f"https://pollinations.ai/p/{clean_prompt}?width=1024&height=1024&seed=42&model=flux&nologo=true"
        
        res = requests.get(url, timeout=30)
        
        if res.status_code == 200:
            # Convertimos la imagen binaria en una cadena Base64 limpia
            img_b64 = base64.b64encode(res.content).decode('utf-8')
            return {"image": img_b64}
        else:
            return {"error": "No se pudo generar la imagen"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)