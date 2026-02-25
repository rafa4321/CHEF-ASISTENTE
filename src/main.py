import os
import json
import re
from google import genai
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Usamos el cliente oficial actualizado
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route('/search', methods=['GET'])
def search_recipe():
    query = request.args.get('query', 'pollo')
    try:
        # Forzamos el modelo estable para evitar el 404 de v1beta
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=f"Genera una receta de {query} en JSON puro. Sin markdown."
        )
        
        # Limpieza de seguridad para evitar errores de NoneType
        text_content = response.text if response.text else "{}"
        match = re.search(r'\{.*\}', text_content, re.DOTALL)
        
        if match:
            clean_json = json.loads(match.group(0))
            # Añadimos imagen y normalizamos datos
            recipe_data = {
                "title": clean_json.get("title", query),
                "kcal": str(clean_json.get("kcal", "0")),
                "proteina": str(clean_json.get("proteina", "0")),
                "ingredients": clean_json.get("ingredients", []),
                "instructions": clean_json.get("instructions", []),
                "image_url": f"https://loremflickr.com/800/600/food,{query.replace(' ', ',')}"
            }
            return jsonify([recipe_data])
        
        return jsonify([{"title": "Error de formato"}]), 200

    except Exception as e:
        # Fallback para que la app no reciba un error 500
        print(f"Error: {e}")
        return jsonify([{
            "title": "Error de Conexión",
            "ingredients": ["Revisa tu configuración"],
            "instructions": [str(e)],
            "image_url": ""
        }]), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))