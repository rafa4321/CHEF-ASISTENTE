import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración de la API Key (Render la tomará de tus Env Vars)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prompt estricto para evitar basura en el JSON
        prompt = f"""
        Genera una receta de {query}. 
        Responde ÚNICAMENTE con un JSON puro, sin bloques de código ```json.
        Estructura:
        {{
          "title": "nombre",
          "kcal": "número",
          "proteina": "número",
          "ingredients": ["lista"],
          "instructions": ["lista"]
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Limpieza de seguridad para evitar el Error 500 al parsear JSON
        raw_text = response.text.strip()
        if "```" in raw_text:
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        
        receta_data = json.loads(raw_text)

        # Imagen compatible con Flutter Web (Evita Error 403)
        # Usamos LoremFlickr que es abierto y no requiere headers prohibidos
        titulo_plato = receta_data.get('title', query).replace(" ", ",")
        image_url = f"[https://loremflickr.com/800/600/food](https://loremflickr.com/800/600/food),{titulo_plato}"

        # Formato de lista que tu App espera: data[0]
        return jsonify([{
            "title": receta_data.get("title", "Receta"),
            "kcal": str(receta_data.get("kcal", "0")),
            "proteina": str(receta_data.get("proteina", "0")),
            "ingredients": receta_data.get("ingredients", []),
            "instructions": receta_data.get("instructions", []),
            "image_url": image_url
        }])

    except Exception as e:
        # Esto imprimirá el error real en los Logs de Render para que lo veamos
        print(f"DEBUG ERROR: {str(e)}")
        return jsonify({"error": "Error procesando la receta"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)