import os
import json
import re
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', 'comida')
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Receta de {query} en JSON.")
        
        # Intentamos extraer el JSON
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
        else:
            raise ValueError("No JSON found")

        return jsonify([data])

    except Exception:
        # ALTERNATIVA DE RESPALDO: Si la IA falla, enviamos esto para PROBAR que el servidor sirve
        return jsonify([{
            "title": f"Receta de prueba para {query}",
            "kcal": "100",
            "proteina": "10",
            "ingredients": ["Ingrediente de prueba"],
            "instructions": ["Paso de prueba"],
            "image_url": "https://loremflickr.com/320/240/food"
        }])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))