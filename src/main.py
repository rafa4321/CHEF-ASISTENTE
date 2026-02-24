import os
import json
import re  # Esta librería es la que hace la "limpieza"
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

# 1. Configuración de la aplicación
app = Flask(__name__)
CORS(app)  # Crucial para que Flutter Web pueda conectarse

# 2. Configuración de Gemini
# Render leerá la clave de las Variables de Entorno
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    
    if not query:
        return jsonify({"error": "No se proporcionó una búsqueda"}), 400

    try:
        # Llamada al modelo Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Le pedimos el JSON, pero estamos preparados por si envía texto extra
        prompt = f"""
        Genera una receta para: {query}.
        Responde estrictamente con un objeto JSON que tenga esta estructura:
        {{
          "title": "nombre del plato",
          "kcal": "valor numérico",
          "proteina": "valor numérico",
          "ingredients": ["lista de ingredientes"],
          "instructions": ["pasos de preparación"]
        }}
        """

        response = model.generate_content(prompt)
        raw_text = response.text

        # --- PASO CRÍTICO: EL FILTRO INTELIGENTE (REGEX) ---
        # Buscamos el contenido que está entre la primera '{' y la última '}'
        # Esto ignora saludos, despedidas o bloques de código Markdown (```json)
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if not match:
            print(f"Texto bruto de la IA: {raw_text}")
            return jsonify({"error": "La IA no devolvió un formato JSON válido"}), 500

        # Extraemos el texto limpio y lo convertimos a un diccionario de Python
        clean_json_text = match.group(0)
        receta_dict = json.loads(clean_json_text)

        # 3. GENERACIÓN DE IMAGEN SEGURA
        # Usamos LoremFlickr porque es compatible con los permisos de Chrome/Flutter Web
        nombre_plato = receta_dict.get('title', query).replace(" ", ",")
        image_url = f"[https://loremflickr.com/800/600/food](https://loremflickr.com/800/600/food),{nombre_plato}"

        # 4. Formato final para Flutter
        # Devolvemos una LISTA que contiene el OBJETO, tal como espera tu app
        resultado = [{
            "title": receta_dict.get("title", "Receta no encontrada"),
            "kcal": str(receta_dict.get("kcal", "0")),
            "proteina": str(receta_dict.get("proteina", "0")),
            "ingredients": receta_dict.get("ingredients", []),
            "instructions": receta_dict.get("instructions", []),
            "image_url": image_url
        }]

        return jsonify(resultado)

    except Exception as e:
        # Si algo falla, lo imprimimos en los logs de Render para saber qué fue
        print(f"ERROR EN EL SERVIDOR: {str(e)}")
        return jsonify({"error": "Error interno al procesar la receta", "details": str(e)}), 500

# 5. Punto de entrada para el servidor
if __name__ == '__main__':
    # Render usa el puerto 10000 por defecto
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)