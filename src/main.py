import os
import json
import re  # Fundamental para limpiar la respuesta
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración con variable de entorno para Render
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "No query"}), 400

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Genera una receta de {query}. 
        Responde exclusivamente en formato JSON con estas llaves: 
        title, kcal, proteina, ingredients (lista), instructions (lista).
        """
        
        response = model.generate_content(prompt)
        raw_text = response.text

        # --- EL EXTRACTOR MÁGICO ---
        # Busca cualquier cosa que empiece con { y termine con }
        match = re.search(r'(\{.*\}|\[.*\])', raw_text, re.DOTALL)
        if match:
            clean_content = match.group(0)
            receta_data = json.loads(clean_content)
        else:
            # Si no hay llaves, algo salió muy mal con la IA
            raise ValueError("No se encontró formato JSON en la respuesta")

        # Imagen: Usamos LoremFlickr (No da error 403 en Chrome)
        search_term = receta_data.get('title', query).replace(" ", ",")
        image_url = f"https://loremflickr.com/800/600/food,{search_term}"

        # Enviamos la lista que espera Flutter
        return jsonify([{
            "title": receta_data.get("title", "Receta"),
            "kcal": str(receta_data.get("kcal", "0")),
            "proteina": str(receta_data.get("proteina", "0")),
            "ingredients": receta_data.get("ingredients", []),
            "instructions": receta_data.get("instructions", []),
            "image_url": image_url
        }])

    except Exception as e:
        print(f"ERROR INTERNO: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)