import os
import json
import re
from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración del cliente con API Key desde entorno
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route('/search', methods=['GET'])
def search_recipe():
    query = request.args.get('query', 'comida')
    try:
        # Prompt optimizado para recibir JSON puro
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=f"Genera una receta de {query} en JSON puro. Campos: title, kcal, proteina, ingredients (lista), instructions (lista)."
        )
        
        # Limpieza de seguridad para el texto recibido
        text = response.text if response.text else ""
        match = re.search(r'\{.*\}', text, re.DOTALL)
        
        if match:
            data = json.loads(match.group(0))
            return jsonify([{
                "title": data.get("title", query),
                "kcal": str(data.get("kcal", "N/A")),
                "proteina": str(data.get("proteina", "N/A")),
                "ingredients": data.get("ingredients", []),
                "instructions": data.get("instructions", []),
                "image_url": f"https://loremflickr.com/800/600/food,{query.replace(' ', ',')}"
            }]), 200
        else:
            raise ValueError("Formato de respuesta inválido")

    except Exception as e:
        # Fallback para que la app siempre reciba una estructura válida
        return jsonify([{
            "title": "Error al obtener receta",
            "ingredients": ["No se pudo conectar con el Chef IA"],
            "instructions": [str(e)],
            "image_url": ""
        }]), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))