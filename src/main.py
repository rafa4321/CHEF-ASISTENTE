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
    query = request.args.get('query', '')
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Prompt de control total
        prompt = f"Genera una receta de {query}. Responde ÚNICAMENTE el JSON puro. Sin ```json ni texto."
        response = model.generate_content(prompt)
        
        # LIMPIEZA MAESTRA: Extraemos solo lo que está entre llaves {}
        text = response.text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            clean_json = match.group(0)
            data = json.loads(clean_json)
        else:
            raise Exception("No se encontró JSON válido")

        # Imagen: Sin proxies, carga directa desde CDN público
        plato = data.get('title', 'food').replace(" ", ",")
        image_url = f"[https://loremflickr.com/800/600/food](https://loremflickr.com/800/600/food),{plato}"

        return jsonify([{
            "title": data.get("title", "Receta"),
            "kcal": str(data.get("kcal", "0")),
            "proteina": str(data.get("proteina", "0")),
            "ingredients": data.get("ingredients", []),
            "instructions": data.get("instructions", []),
            "image_url": image_url
        }])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))