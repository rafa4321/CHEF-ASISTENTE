import os
import json
import re
from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# El cliente 'genai.Client' usa por defecto la versión estable v1, evitando el error 404 de v1beta
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route('/search', methods=['GET'])
def search_recipe():
    query = request.args.get('query', 'asado')
    try:
        # Forzamos el modelo gemini-1.5-flash que es el más estable en tu región
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Dame una receta de {query} en formato JSON. Usa exactamente estas llaves: title, kcal, proteina, ingredients (lista), instructions (lista). No uses markdown."
        )
        
        # Validamos que response.text no sea None para evitar el error de Pylance
        raw_text = response.text if response.text else "{}"
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if match:
            data = json.loads(match.group(0))
            # Construcción segura para evitar errores de tipo en Flutter
            return jsonify([{
                "title": str(data.get("title", query)),
                "kcal": str(data.get("kcal", "0")),
                "proteina": str(data.get("proteina", "0")),
                "ingredients": data.get("ingredients", []),
                "instructions": data.get("instructions", []),
                "image_url": f"https://loremflickr.com/800/600/food,{query.replace(' ', ',')}"
            }]), 200
        else:
            raise ValueError("Respuesta de IA sin formato JSON")

    except Exception as e:
        # Fallback para que la App siempre reciba datos y no se quede en blanco
        return jsonify([{
            "title": "Chef en mantenimiento",
            "instructions": [f"Error técnico: {str(e)}"],
            "ingredients": ["Reintentando conexión..."],
            "image_url": ""
        }]), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))