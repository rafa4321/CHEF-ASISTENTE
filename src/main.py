import os
import json
import re
from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración del Cliente con modelo estable
MODEL_ID = "gemini-1.5-flash"
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route('/', methods=['GET'])
def health():
    """Ruta para que Render verifique que el servicio está vivo"""
    return jsonify({"status": "ready", "model": MODEL_ID, "service": "Chef AI"}), 200

@app.route('/search', methods=['GET'])
def search_recipe():
    query = request.args.get('query', 'comida venezolana')
    
    try:
        # Prompt optimizado para respuesta JSON pura
        prompt = (f"Actúa como un Chef profesional. Genera una receta de {query} "
                  "estrictamente en formato JSON con estas llaves: "
                  "title, kcal, proteina, ingredients (lista), instructions (lista). "
                  "No incluyas markdown, ni bloques de código, ni texto adicional.")
        
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )
        
        raw_text = response.text if response.text else ""
        
        # Extracción de seguridad con Regex (por si la IA envía texto extra)
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if match:
            data = json.loads(match.group(0))
        else:
            raise ValueError("La IA no devolvió un formato JSON válido")

        # Formato final sincronizado con el modelo de Flutter
        return jsonify([{
            "title": data.get("title", query),
            "kcal": str(data.get("kcal", "N/A")),
            "proteina": str(data.get("proteina", "N/A")),
            "ingredients": data.get("ingredients", []),
            "instructions": data.get("instructions", []),
            "image_url": f"https://loremflickr.com/800/600/food,{query.replace(' ', ',')}"
        }]), 200

    except Exception as e:
        print(f"Error en servidor: {e}")
        return jsonify([{
            "title": "Error de Conexión",
            "kcal": "0",
            "proteina": "0",
            "ingredients": ["No se pudo obtener la receta"],
            "instructions": [f"Detalle técnico: {str(e)}"],
            "image_url": ""
        }]), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)