import os
import json
import re
from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Usamos 1.5-flash porque es el que tu Render permite (vimos el 404 del 2.0)
MODEL_ID = "gemini-1.5-flash"
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "ready"}), 200

@app.route('/search', methods=['GET'])
def search_recipe():
    query = request.args.get('query', 'comida')
    try:
        # Prompt de alta restricción
        prompt = (f"Genera una receta de {query} en JSON puro. "
                  "Estructura: {'title': '', 'kcal': '', 'proteina': '', 'ingredients': [], 'instructions': []}. "
                  "No escribas NADA fuera del JSON, sin markdown.")
        
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        
        # LIMPIEZA TOTAL: Extraemos solo lo que está entre llaves { }
        raw_text = response.text if response.text else ""
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if match:
            clean_json = json.loads(match.group(0))
            # Inyectamos la imagen para la UI
            clean_json["image_url"] = f"https://loremflickr.com/800/600/food,{query.replace(' ', ',')}"
            return jsonify([clean_json]), 200 # Enviamos como lista [ ]
        else:
            raise ValueError("La IA no envió JSON")

    except Exception as e:
        print(f"DEBUG: {e}")
        return jsonify([{"title": "Error", "instructions": [str(e)], "ingredients": [], "image_url": ""}]), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))