import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

# 1. Inicialización de la App
app = Flask(__name__)
CORS(app)  # Permite que Flutter Web acceda a la API sin bloqueos

# 2. Configuración de Gemini
# Render leerá la variable de entorno GOOGLE_API_KEY
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "TU_CLAVE_AQUI_PARA_LOCAL")
genai.configure(api_key=GOOGLE_API_KEY)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    
    if not query:
        return jsonify({"error": "No se proporcionó búsqueda"}), 400

    try:
        # Configuración del modelo
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prompt optimizado para evitar texto extra
        prompt = f"""
        Actúa como un chef profesional. Genera una receta detallada para: {query}.
        Responde ÚNICAMENTE con un objeto JSON válido que contenga:
        "title": nombre del plato,
        "kcal": número aproximado,
        "proteina": gramos de proteína,
        "ingredients": lista de strings,
        "instructions": lista de pasos.
        No incluyas etiquetas markdown como ```json o texto adicional.
        """

        response = model.generate_content(prompt)
        
        # Limpieza profunda del texto recibido por si Gemini usa Markdown
        raw_text = response.text.strip()
        if "```" in raw_text:
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        
        # Convertir texto a diccionario de Python
        receta_json = json.loads(raw_text)

        # 3. GENERACIÓN DE IMAGEN (Solución real al error 403)
        # Usamos un CDN público que permite acceso desde Flutter Web
        nombre_plato = receta_json.get('title', query).replace(" ", ",")
        image_url = f"[https://loremflickr.com/800/600/food](https://loremflickr.com/800/600/food),{nombre_plato}"

        # 4. Respuesta en el formato que espera tu App de Flutter (Lista [data[0]])
        resultado = [{
            "title": receta_json.get("title", "Receta no encontrada"),
            "kcal": str(receta_json.get("kcal", "0")),
            "proteina": str(receta_json.get("proteina", "0")),
            "ingredients": receta_json.get("ingredients", []),
            "instructions": receta_json.get("instructions", []),
            "image_url": image_url
        }]

        return jsonify(resultado)

    except Exception as e:
        print(f"Error en el servidor: {str(e)}")
        return jsonify({"error": "Error interno al procesar la receta"}), 500

# 5. Ejecución local
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)