import os
import json
import re
from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración del cliente sin forzar versiones beta
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route('/search', methods=['GET'])
def search_recipe():
    query = request.args.get('query', 'asado')
    try:
        # Llamada directa al modelo estable
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Dame una receta de {query} en JSON puro. Sin markdown."
        )
        
        # Validación de seguridad para evitar errores de NoneType
        text_content = response.text if response.text else "{}"
        match = re.search(r'\{.*\}', text_content, re.DOTALL)
        
        if match:
            recipe_json = json.loads(match.group(0))
            return jsonify([{
                "title": str(recipe_json.get("title", query)),
                "kcal": str(recipe_json.get("kcal", "0")),
                "proteina": str(recipe_json.get("proteina", "0")),
                "ingredients": recipe_json.get("ingredients", []),
                "instructions": recipe_json.get("instructions", []),
                "image_url": f"https://loremflickr.com/800/600/food,{query.replace(' ', ',')}"
            }]), 200
        
        raise ValueError("No se recibió un JSON válido")

    except Exception as e:
        # Respuesta de emergencia profesional
        return jsonify([{
            "title": "Chef reconectando...",
            "instructions": [f"Error: {str(e)}"],
            "ingredients": ["Reintentando conexión con Gemini"],
            "image_url": ""
        }]), 200