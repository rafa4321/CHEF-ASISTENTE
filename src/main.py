from fastapi import FastAPI, HTTPException
from groq import Groq
import os

app = FastAPI()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.get("/search")
async def search_recipe(query: str):
    try:
        chat_completion = client.chat.completions.create(
            # Usamos el modelo actualizado que ya tienes funcionando
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": """Eres un Chef Profesional de nivel Michelin. 
                    REGLA ESTRICTA: Solo puedes responder sobre recetas, ingredientes y técnicas de cocina.
                    Si el usuario pregunta sobre motores, política, tecnología o cualquier tema ajeno a la comida, 
                    debes responder: 'Lo siento, como tu Chef Asistente, solo puedo ayudarte con temas culinarios.'
                    Responde siempre en formato JSON con las llaves: 'nombre', 'ingredientes' (lista) e 'instrucciones' (texto)."""
                },
                {
                    "role": "user", 
                    "content": query
                }
            ],
            response_format={"type": "json_object"}
        )
        
        # Validación de respuesta
        if not chat_completion.choices:
            raise HTTPException(status_code=500, detail="La IA no devolvió respuesta")
            
        return chat_completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))