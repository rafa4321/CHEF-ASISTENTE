from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Asegúrate de importar tu lógica de IA aquí (ejemplo: OpenAI o LangChain)

app = FastAPI()

# Esto permite que tu localhost hable con Render sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
async def search_recipe(query: str):
    # AQUÍ LLAMAS A TU IA
    # Ejemplo de cómo debería estructurarse la respuesta:
    
    # receta_ia = tu_funcion_ia(query) 
    
    return {
        "title": f"Receta de {query}", # Flutter buscará 'title'
        "ingredients": [
            "Ingrediente real 1",
            "Ingrediente real 2",
            "Ingrediente real 3"
        ],
        "instructions": [
            "Paso 1: Preparar los utensilios.",
            "Paso 2: Mezclar los ingredientes.",
            "Paso 3: Cocinar a fuego lento."
        ],
        "description": f"Una deliciosa forma de preparar {query}."
    }