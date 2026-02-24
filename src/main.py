import os
import json
import re
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración de Gemini
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "Falta la consulta"}), 400

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Genera una receta de {query}. 
        Responde ÚNICAMENTE con un objeto JSON válido.
        Estructura: {{"title": "", "kcal": "", "proteina": "", "ingredients": [], "instructions": []}}
        """
        
        response = model.generate_content(prompt)
        raw_text = response.text

        # --- EL FILTRO DE SEGURIDAD (REGEX) ---
        # Buscamos el bloque de llaves {} para ignorar cualquier texto extra de la IA
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if not match:
            raise ValueError("La IA no generó un JSON válido")

        receta_data = json.loads(match.group(0))

        # Imagen: Usamos LoremFlickr para evitar el Error 403 de Chrome
        search_term = receta_data.get('title', query).replace(" ", ",")
        image_url = f"https://loremflickr.com/800/600/food,{search_term}"

        # Enviamos la lista [data[0]] que espera Flutter
        return jsonify([{
            "title": receta_data.get("title", "Receta"),
            "kcal": str(receta_data.get("kcal", "0")),
            "proteina": str(receta_data.get("proteina", "0")),
            "ingredients": receta_data.get("ingredients", []),
            "instructions": receta_data.get("instructions", []),
            "image_url": image_url
        }])

    except Exception as e:
        print(f"Error en servidor: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)