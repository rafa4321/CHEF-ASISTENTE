import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Asegúrate de que esta variable esté en Render -> Settings -> Environment
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "No query"}), 400

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Pedimos el formato pero con un "seguro" de texto
        prompt = f"Genera una receta de {query}. Responde SOLO el objeto JSON con: title, kcal, proteina, ingredients[], instructions[]. Sin explicaciones."
        
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # --- AQUÍ ESTÁ EL AVANCE: LIMPIEZA TOTAL ---
        # Si Gemini manda ```json ... ``` lo eliminamos manualmente
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            # Quitamos la primera línea (```json) y la última (```)
            raw_text = "\n".join(lines[1:-1]) if "json" in lines[0] else "\n".join(lines[1:-1])
        
        # Intentamos cargar el JSON ya limpio
        receta_dict = json.loads(raw_text)

        # Imagen: Usamos una URL directa que no use proxies conflictivos
        plato = receta_dict.get('title', query).replace(" ", ",")
        image_url = f"https://loremflickr.com/800/600/food,{plato}"

        return jsonify([{
            "title": receta_dict.get("title"),
            "kcal": str(receta_dict.get("kcal")),
            "proteina": str(receta_dict.get("proteina")),
            "ingredients": receta_dict.get("ingredients"),
            "instructions": receta_dict.get("instructions"),
            "image_url": image_url
        }])

    except Exception as e:
        # Esto nos dirá exactamente qué rompió el JSON en los logs de Render
        print(f"FALLO CRÍTICO: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)