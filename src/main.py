import os
import json
import re
from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Configuración de CORS total para evitar bloqueos en la App
CORS(app, resources={r"/*": {"origins": "*"}})

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "ready"}), 200

@app.route('/search', methods=['GET'])
def search_recipe():
    query = request.args.get('query', 'comida')
    try:
        # Usamos 1.5-flash por estabilidad comprobada en tu instancia de Render
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Genera una receta de {query} en JSON puro. Llaves: title, kcal, proteina, ingredients (lista), instructions (lista). Sin markdown."
        )
        
        raw_text = response.text if response.text else ""
        # Limpieza extrema de caracteres no-JSON
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if match:
            data = json.loads(match.group(0))
        else:
            raise ValueError("No se encontró JSON")

        # Construcción del objeto final
        recipe = {
            "title": data.get("title", query).capitalize(),
            "kcal": str(data.get("kcal", "N/A")),
            "proteina": str(data.get("proteina", "N/A")),
            "ingredients": data.get("ingredients", []),
            "instructions": data.get("instructions", []),
            "image_url": f"https://loremflickr.com/800/600/food,{query.replace(' ', ',')}"
        }
        return jsonify([recipe]), 200

    except Exception as e:
        # Fallback: Si todo falla, enviamos este objeto para que la app NO se quede en blanco
        print(f"Error detectado: {e}")
        return jsonify([{
            "title": "Chef temporalmente ausente",
            "kcal": "0",
            "proteina": "0",
            "ingredients": ["Revisa tu conexión a internet"],
            "instructions": ["Inténtalo de nuevo en unos segundos."],
            "image_url": "https://via.placeholder.com/800x600?text=Error+de+Conexion"
        }]), 200 # Enviamos 200 para que la app no explote

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))