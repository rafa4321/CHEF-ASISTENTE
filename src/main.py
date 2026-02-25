import os
import json
import re
from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Permitimos CORS para que Flutter Web/Mobile no tenga bloqueos
CORS(app, resources={r"/*": {"origins": "*"}})

# Usamos 1.5-flash por estabilidad (visto error 404 en 2.0 en tus logs)
MODEL_ID = "gemini-1.5-flash"
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "online", "model": MODEL_ID}), 200

@app.route('/search', methods=['GET'])
def search_recipe():
    query = request.args.get('query', 'comida')
    try:
        # Prompt optimizado para JSON
        prompt = (f"Genera una receta de {query} en JSON puro. "
                  "Campos: title, kcal, proteina, ingredients (lista), instructions (lista). "
                  "No uses markdown ni texto extra.")
        
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        
        # Limpieza de seguridad para evitar errores de tipo (NoneType)
        raw_text = response.text if response.text else ""
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if match:
            data = json.loads(match.group(0))
            return jsonify([{
                "title": data.get("title", query).capitalize(),
                "kcal": str(data.get("kcal", "N/A")),
                "proteina": str(data.get("proteina", "N/A")),
                "ingredients": data.get("ingredients", []),
                "instructions": data.get("instructions", []),
                "image_url": f"https://loremflickr.com/800/600/food,{query.replace(' ', ',')}"
            }]), 200
        else:
            raise ValueError("No se pudo parsear el JSON de la IA")

    except Exception as e:
        print(f"Error técnico: {e}")
        return jsonify([{
            "title": "Chef en pausa",
            "ingredients": ["Verificar API Key o conexión"],
            "instructions": [str(e)],
            "image_url": ""
        }]), 200 # Enviamos 200 para que la App no rompa el flujo

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)