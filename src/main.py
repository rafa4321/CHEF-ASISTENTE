import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configura tu clave directamente para pruebas locales si es necesario
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "TU_CLAVE_AQUI")
genai.configure(api_key=GOOGLE_API_KEY)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "No query"}), 400

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Pedimos JSON puro para evitar errores de lectura
        prompt = f"Dame una receta de {query} en JSON con: title, kcal, proteina, ingredients[], instructions[]. Sin texto extra."
        response = model.generate_content(prompt)
        
        # Limpieza de Markdown si Gemini lo incluye
        clean_text = response.text.strip().replace("```json", "").replace("```", "")
        receta = json.loads(clean_text)

        # Usamos LoremFlickr: es la ÚNICA que no da error 403 en Chrome
        titulo_slug = receta.get('title', query).replace(" ", ",")
        image_url = f"https://loremflickr.com/800/600/food,{titulo_slug}"

        return jsonify([{
            "title": receta.get("title"),
            "kcal": receta.get("kcal"),
            "proteina": receta.get("proteina"),
            "ingredients": receta.get("ingredients"),
            "instructions": receta.get("instructions"),
            "image_url": image_url
        }])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))