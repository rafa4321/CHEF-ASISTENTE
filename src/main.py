import os
import json
import re
from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Cliente configurado para la versión estable de producción
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route('/search', methods=['GET'])
def search_recipe():
    query = request.args.get('query', 'asado')
    try:
        # Usamos 1.5-flash: el más rápido y estable disponible en Uruguay
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Genera una receta de {query} en JSON puro. Campos: title, kcal, proteina, ingredients, instructions."
        )
        
        # Validación crítica para evitar errores de 'NoneType'
        raw_text = response.text if response.text else ""
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if match:
            data = json.loads(match.group(0))
            return jsonify([{
                "title": data.get("title", query),
                "kcal": str(data.get("kcal", "0")),
                "proteina": str(data.get("proteina", "0")),
                "ingredients": data.get("ingredients", []),
                "instructions": data.get("instructions", []),
                "image_url": f"https://loremflickr.com/800/600/food,{query.replace(' ', ',')}"
            }]), 200
        else:
            raise ValueError("Formato de respuesta inválido")

    except Exception as e:
        # Respuesta controlada para que la App no se cierre
        return jsonify([{
            "title": "Error de Conexión",
            "instructions": [f"Detalle técnico: {str(e)}"],
            "ingredients": ["Verifica tu API Key en Google AI Studio"],
            "image_url": ""
        }]), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))