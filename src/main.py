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
            contents=f"Genera una receta de {query} en JSON puro con estos campos: title, kcal, proteina, ingredients[], instructions[]. Sin texto extra."
        )
        
        raw_text = response.text if response.text else ""
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if match:
            data = json.loads(match.group(0))
        else:
            raise ValueError("No JSON found")

        # Sincronizado con tu modelo de Flutter:
        return jsonify([{
            "title": data.get("title", query),
            "kcal": str(data.get("kcal", "0")),
            "proteina": str(data.get("proteina", "0")),
            "ingredients": data.get("ingredients", []),
            "instructions": data.get("instructions", []),
            "image_url": f"https://loremflickr.com/800/600/food,{query.replace(' ', ',')}"
        }])

    except Exception as e:
        print(f"Error: {e}")
        # Retorno de emergencia para romper el loop
        return jsonify([{
            "title": "Error de carga",
            "kcal": "0",
            "proteina": "0",
            "ingredients": ["No se pudo obtener la receta"],
            "instructions": [str(e)],
            "image_url": ""
        }])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))