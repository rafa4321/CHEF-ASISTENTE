import os
import json
import re
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración de API Key (Render la toma de Environment Variables)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "No query"}), 400

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Genera una receta de {query} en JSON puro con: title, kcal, proteina, ingredients[], instructions[]. Sin texto extra."
        response = model.generate_content(prompt)
        
        # EXTRACTOR REGEX: Busca el bloque de llaves { ... }
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if not match:
            raise ValueError("No se encontró JSON en la respuesta de la IA")
            
        data = json.loads(match.group(0))

        # URL de imagen que NO da error 403 en Flutter Web
        search_term = data.get('title', query).replace(" ", ",")
        image_url = f"https://loremflickr.com/800/600/food,{search_term}"

        # Formato de lista [data[0]] que espera tu Flutter
        return jsonify([{
            "title": data.get("title", "Receta"),
            "kcal": str(data.get("kcal", "0")),
            "proteina": str(data.get("proteina", "0")),
            "ingredients": data.get("ingredients", []),
            "instructions": data.get("instructions", []),
            "image_url": image_url
        }])
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)