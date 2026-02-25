import os
import json
import re
from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración para Gemini 3 Flash
# Nota: Asegúrate de que tu entorno tenga instalada la última versión de google-genai
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
MODEL_ID = "gemini-3-flash"

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "online", "model": MODEL_ID}), 200

@app.route('/search', methods=['GET'])
def search_recipe():
    query = request.args.get('query', 'receta')
    try:
        # Prompt estructurado para JSON puro
        prompt = (f"Genera una receta de {query} en formato JSON. "
                  "Usa estas llaves: title, kcal, proteina, ingredients (lista), instructions (lista). "
                  "No incluyas explicaciones ni formato markdown.")
        
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        
        # Limpieza de seguridad para evitar errores de tipo detectados en VS Code
        raw_text = response.text if response.text else ""
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if match:
            data = json.loads(match.group(0))
            # Construcción del objeto final para Flutter
            return jsonify([{
                "title": data.get("title", query),
                "kcal": str(data.get("kcal", "N/A")),
                "proteina": str(data.get("proteina", "N/A")),
                "ingredients": data.get("ingredients", []),
                "instructions": data.get("instructions", []),
                "image_url": f"https://loremflickr.com/800/600/food,{query.replace(' ', ',')}"
            }]), 200
        else:
            raise ValueError("La IA no devolvió un formato JSON válido")

    except Exception as e:
        # Fallback de seguridad para que la app no reciba un error 500
        return jsonify([{
            "title": "Chef en pausa",
            "ingredients": ["Error de comunicación"],
            "instructions": [str(e)],
            "image_url": ""
        }]), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)