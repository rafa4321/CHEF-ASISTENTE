import os
import json
import re
from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Inicializamos con la nueva librería
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route('/search', methods=['GET'])
def search_recipe():
    query = request.args.get('query', 'comida')
    
    try:
        # Forzamos a la IA a ser breve
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Genera una receta de {query} en JSON puro con: title, kcal, proteina, ingredients[], instructions[]. No escribas nada más."
        )
        
        # Validación de texto para evitar el error 'None'
        raw_text = response.text if response.text else ""
        
        # Buscamos el bloque JSON entre llaves { }
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        
        if match:
            data = json.loads(match.group(0))
        else:
            # Si la IA falla, creamos una respuesta coherente
            raise ValueError("Formato JSON no detectado")

        # Retornamos una LISTA [] para que Flutter sea feliz
        return jsonify([{
            "title": data.get("title", query).upper(),
            "kcal": str(data.get("kcal", "0")),
            "proteina": str(data.get("proteina", "0")),
            "ingredients": data.get("ingredients", ["Ingredientes no disponibles"]),
            "instructions": data.get("instructions", ["Pasos no disponibles"]),
            "image_url": f"https://loremflickr.com/800/600/food,{query.replace(' ', ',')}"
        }])

    except Exception as e:
        print(f"Error en servidor: {e}")
        # Respuesta de emergencia: esto rompe el loop de carga en la App
        return jsonify([{
            "title": "ERROR DE CONEXIÓN",
            "kcal": "0", "proteina": "0",
            "ingredients": ["No se pudo conectar con la IA"],
            "instructions": ["Por favor, intenta de nuevo"],
            "image_url": ""
        }])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)