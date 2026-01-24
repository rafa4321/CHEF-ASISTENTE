# Archivo: recipes/api.py (Nuevo Endpoint)

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from ..third_party.gemini_client import GeminiClient
from .services import RecipeService # Servicio que maneja la lógica de negocio

router = APIRouter(prefix="/recipes")

@router.post("/analyze-image", response_model=RecipeSchema) # RecipeSchema es el molde de respuesta
async def analyze_and_generate(
    pantry_image: UploadFile = File(...), # El Backend espera un archivo llamado 'pantry_image'
    user_tier: str,
    # Asume que tenemos un token de usuario y el cliente de Gemini
    gemini_client: GeminiClient = Depends(get_gemini_client) 
):
    # 1. Guardar la imagen temporalmente para que Gemini pueda acceder a ella
    temp_file_path = f"/tmp/{pantry_image.filename}"
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await pantry_image.read())
        
    # 2. Llamar a nuestro cliente de Gemini para identificar los ingredientes
    # Esta es la magia de la IA: GeminiClient.analyze_image_for_ingredients
    identified_ingredients = gemini_client.analyze_image_for_ingredients(
        image_path=temp_file_path, 
        context="Genera una lista de ingredientes comestibles visibles en una nevera."
    )
    
    # 3. Limpiar el archivo temporal
    os.remove(temp_file_path)

    if not identified_ingredients:
        raise HTTPException(status_code=400, detail="GEMINI_NO_INGREDIENTS")

    # 4. Usar los ingredientes identificados para generar la receta
    # Llamamos al servicio de generación de recetas, ¡pero con la lista de la IA!
    recipe_data = RecipeService.generate_recipe_from_list(
        ingredients=identified_ingredients,
        user_tier=user_tier
    )

    return recipe_data # Devuelve la receta generada en el molde (Schema)