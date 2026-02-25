import os
import json
import re
from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite que tu app Flutter (Web/Mobile) acceda sin bloqueos

# Configuración del cliente Google AI Studio
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route('/', methods=['GET'])
def health():
    """Ruta necesaria para que Render sepa que el servidor está vivo"""
    return jsonify({"status": "ready", "service": "Chef AI API"}), 200

@app.route('/search', methods=['GET'])
def search_recipe():
    query = request.args.get('query', 'Receta sorpresa')
    
    try:
        # Prompt de ingeniería de alta precisión
        prompt = (
            f"Actúa como un Chef experto. Genera una receta de '{query}' únicamente en formato JSON. "
            "Usa exactamente estas llaves: title, kcal, proteina, ingredients (lista), instructions (lista). "
            "No incluyas markdown (```json), ni texto antes o después del objeto JSON."
        )
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        raw_text = response.text if response.text else ""
        
        # Verificación profunda: Extracción por Regex por si Gemini envía Markdown
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if json_match:
            clean_json = json.loads(json_match.group(0))
        else:
            raise ValueError("La IA no devolvió un JSON válido")

        # Construcción de la respuesta final sincronizada con Flutter
        recipe_data = {
            "title": clean_json.get("title", query),
            "kcal": str(clean_json.get("kcal", "N/A")),
            "proteina": str(clean_json.get("proteina", "N/A")),
            "ingredients": clean_json.get("ingredients", []),
            "instructions": clean_json.get("instructions", []),
            "image_url": f"[https://loremflickr.com/800/600/food](https://loremflickr.com/800/600/food),{query.replace(' ', ',')}"
        }

        return jsonify([recipe_data]), 200

    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        # Respuesta de emergencia profesional
        return jsonify([{
            "title": "Chef ocupado",
            "kcal": "0",
            "proteina": "0",
            "ingredients": ["No pudimos conectar con el servidor"],
            "instructions": [f"Error técnico: {str(e)}"],
            "image_url": ""
        }]), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)