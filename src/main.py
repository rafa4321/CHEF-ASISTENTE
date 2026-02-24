import os
import json
import re  # Necesario para limpiar la respuesta de la IA
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración de Gemini
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
        raw_text = response.text

        # --- FILTRO REGEX ---
        # Busca el bloque de llaves {} para evitar el Error 500 si la IA escribe texto extra
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if not match:
            raise ValueError("No se encontró JSON válido")

        data = json.loads(match.group(0))

        # Imagen: LoremFlickr es compatible con Chrome y no da Error 403
        search_term = data.get('title', query).replace(" ", ",")
        image_url = f"https://loremflickr.com/800/600/food,{search_term}"

        # Enviamos la lista [data] que espera tu código de Flutter
        return jsonify([{
            "title": data.get("title", "Receta"),
            "kcal": str(data.get("kcal", "0")),
            "proteina": str(data.get("proteina", "0")),
            "ingredients": data.get("ingredients", []),
            "instructions": data.get("instructions", []),
            "image_url": image_url
        }])

    except Exception as e:
        print(f"Error detectado: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)