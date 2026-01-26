from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
import os

app = FastAPI()

# Permitir que tu App de Flutter se conecte
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de Groq
# Asegúrate de que GROQ_API_KEY esté en las variables de entorno de Render
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.get("/")
def home():
    return {"message": "Chef Asistente API is Online", "status": "ok"}

@app.get("/search")
def search_recipe(query: str):
    try:
        # Llamada a la IA de Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Eres un chef experto. Responde siempre en formato JSON con las llaves: nombre, ingredientes (lista), instrucciones (texto)."
                },
                {
                    "role": "user",
                    "content": f"Dame una receta de: {query}"
                }
            ],
            model="llama-3.3-70b-versatile" ,
            response_format={"type": "json_object"} # Forzamos respuesta JSON
        )

        # VALIDACIÓN CRÍTICA: Verificamos si existen 'choices' antes de acceder
        if not chat_completion.choices or len(chat_completion.choices) == 0:
            raise HTTPException(status_code=500, detail="La IA no devolvió resultados")

        # Extraemos el contenido
        receta_raw = chat_completion.choices[0].message.content
        return [eval(receta_raw)] # Convertimos el texto en objeto JSON para la App

    except Exception as e:
        # Esto nos dirá exactamente qué falla en los logs de Render
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)