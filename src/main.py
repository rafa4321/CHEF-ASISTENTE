from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# ... tus otras importaciones

app = FastAPI()

# Configuración de CORS obligatoria para Flutter Web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
async def search_recipe(query: str):
    # ... lógica para obtener la receta de la IA ...
    
    # IMPORTANTE: Devuelve un diccionario, NO un json.dumps()
    return {
        "title": "Nombre de la Receta", # Usa 'title' para coincidir con el Flutter de abajo
        "ingredients": ["ingrediente 1", "ingrediente 2"],
        "instructions": ["paso 1", "paso 2"],
        "description": "Una breve descripción"
    }