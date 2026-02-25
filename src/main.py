import os
import json
import re
from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Usamos la versión estable 1.5 para garantizar el 100% de disponibilidad
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route('/search', methods=['GET'])
def search_recipe():
    query = request.args.get('query', 'receta')
    try:
        # Forzamos a Gemini a responder solo el objeto que necesitamos
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Dame una receta de {query} en JSON puro con title, kcal, proteina, ingredients (lista) y instructions (lista). Sin markdown."
        )
        
        # Limpieza absoluta del texto recibido
        text = response.text if response.text else ""
        match = re.search(r'\{.*\}', text, re.DOTALL)
        
        if match:
            data = json.loads(match.group(0))
            # Estructura que tu App espera
            return jsonify([{
                "title": data.get("title", query),
                "kcal": str(data.get("kcal", "0")),
                "proteina": str(data.get("proteina", "0")),
                "ingredients": data.get("ingredients", []),
                "instructions": data.get("instructions", []),
                "image_url": f"https://loremflickr.com/800/600/food,{query.replace(' ', ',')}"
            }]), 200
        else:
            raise ValueError("Respuesta no válida")

    except Exception as e:
        # Si Gemini falla, el servidor responde con un mensaje amigable, NO con un error 500
        return jsonify([{
            "title": "Chef ocupado",
            "ingredients": ["Intenta de nuevo"],
            "instructions": [str(e)],
            "image_url": ""
        }]), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))