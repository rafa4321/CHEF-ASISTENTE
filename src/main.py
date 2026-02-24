import os
import json
import re
from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route('/search', methods=['GET'])
def search_recipe():
    query = request.args.get('query', 'comida')
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Genera una receta de {query} en JSON puro. Solo el objeto JSON con: title, kcal, proteina, ingredients[], instructions[]. Sin introducciones ni markdown."
        )
        
        # 1. Aseguramos que recibimos texto
        raw_text = response.text if response.text else ""
        
        # 2. VICTORIA: Buscamos el JSON entre las llaves { } ignorando todo lo demás
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if match:
            clean_json = match.group(0)
            data = json.loads(clean_json)
        else:
            raise ValueError("No se encontró un JSON válido en la respuesta")

        # 3. Enviamos la LISTA que Flutter espera
        return jsonify([{
            "title": data.get("title", query),
            "kcal": str(data.get("kcal", "0")),
            "proteina": str(data.get("proteina", "0")),
            "ingredients": data.get("ingredients", []),
            "instructions": data.get("instructions", []),
            "image_url": f"https://loremflickr.com/800/600/food,{query.replace(' ', ',')}"
        }])

    except Exception as e:
        print(f"Error real: {e}")
        # Retorno de emergencia (lo que ves ahora en tu pantalla)
        return jsonify([{
            "title": "Error al procesar",
            "kcal": "0", "proteina": "0",
            "ingredients": ["La IA envió un formato incorrecto"],
            "instructions": [str(e)],
            "image_url": ""
        }])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))