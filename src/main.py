import os
import json
import re
# CORRECCIÓN: La librería se llama 'google-genai' en pip, pero se importa así:
from google import genai 
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# CORRECCIÓN: El cliente se inicializa a través de genai.Client
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "Falta consulta"}), 400

    try:
        # CORRECCIÓN: Estructura de llamada según la nueva librería
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Dame una receta de {query} en JSON puro: {{'title': '...', 'kcal': '...', 'proteina': '...', 'ingredients': [], 'instructions': []}}"
        )
        
        raw_text = response.text
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if not match:
            raise ValueError("No se encontró JSON")

        data = json.loads(match.group(0))
        
        # Devolvemos la LISTA que espera Flutter
        return jsonify([{
            "title": data.get("title", query),
            "kcal": str(data.get("kcal", "0")),
            "proteina": str(data.get("proteina", "0")),
            "ingredients": data.get("ingredients", []),
            "instructions": data.get("instructions", []),
            "image_url": f"https://loremflickr.com/800/600/food,{query.replace(' ', ',')}"
        }])
    except Exception as e:
        return jsonify([{"title": "Error", "ingredients": [str(e)], "instructions": []}]), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))