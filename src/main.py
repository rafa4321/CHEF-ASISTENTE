import os
import json
import re
from google import genai # Importación correcta según logs
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Inicialización segura del cliente
api_key = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

@app.route('/search', methods=['GET'])
def search_recipe(): # Cambié el nombre para evitar conflictos con la librería 're'
    query = request.args.get('query', '')
    if not query:
        return jsonify([{"title": "Error: Consulta vacía"}]), 400

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Genera una receta de {query} en JSON puro con: title, kcal, proteina, ingredients[], instructions[]."
        )
        
        # VALIDACIÓN CRÍTICA: Aseguramos que 'text' exista y sea string
        raw_text = response.text if response.text else ""
        
        # Usamos re.search solo si tenemos texto para evitar el error de tu captura
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if match:
            data = json.loads(match.group(0))
        else:
            raise ValueError("No se pudo extraer el JSON de la respuesta")

        # Formateamos la respuesta como la lista que espera Flutter
        return jsonify([{
            "title": data.get("title", query),
            "kcal": str(data.get("kcal", "0")),
            "proteina": str(data.get("proteina", "0")),
            "ingredients": data.get("ingredients", []),
            "instructions": data.get("instructions", []),
            "image_url": f"https://loremflickr.com/800/600/food,{query.replace(' ', ',')}"
        }])

    except Exception as e:
        print(f"Error detectado: {e}")
        return jsonify([{
            "title": "Error de conexión",
            "kcal": "0", "proteina": "0",
            "ingredients": ["No se pudo obtener la receta"],
            "instructions": [str(e)],
            "image_url": ""
        }]), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))