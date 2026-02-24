import os
import json
import re
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Genera una receta de {query} en JSON puro. Sin texto extra."
        response = model.generate_content(prompt)
        
        # SOLUCIÓN AL ERROR 500: Extraer solo lo que está entre llaves { }
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if not match:
            raise Exception("La IA no envió un JSON válido")
            
        data = json.loads(match.group(0))

        # SOLUCIÓN AL ERROR 403: Usar una fuente que Chrome no bloquee
        plato_url = data.get('title', query).replace(" ", ",")
        image_url = f"[https://loremflickr.com/800/600/food](https://loremflickr.com/800/600/food),{plato_url}"

        return jsonify([{
            "title": data.get("title", "Receta"),
            "kcal": str(data.get("kcal", "0")),
            "proteina": str(data.get("proteina", "0")),
            "ingredients": data.get("ingredients", []),
            "instructions": data.get("instructions", []),
            "image_url": image_url
        }])
    except Exception as e:
        return jsonify({"error": str(e)}), 500