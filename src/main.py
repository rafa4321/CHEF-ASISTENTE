import os
import json
from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Inicializamos el cliente con la nueva librería según tus logs
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.route('/search', methods=['GET'])
def search_recipe():
    query = request.args.get('query', 'comida')
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Genera una receta de {query} en JSON puro con: title, kcal, proteina, ingredients[], instructions[]. Sin texto extra."
        )
        
        # SOLUCIÓN AL ERROR 'None': Forzamos a que sea un string vacío si falla
        raw_text = response.text if response.text else ""
        
        # Limpieza de seguridad
        clean_json = raw_text.replace('```json', '').replace('```', '').strip()
        
        if not clean_json:
            raise ValueError("La IA devolvió un contenido vacío")

        data = json.loads(clean_json)

        # RETORNO: Siempre una lista para que Flutter no explote
        return jsonify([{
            "title": data.get("title", query),
            "kcal": str(data.get("kcal", "0")),
            "proteina": str(data.get("proteina", "0")),
            "ingredients": data.get("ingredients", []),
            "instructions": data.get("instructions", []),
            "image_url": f"https://loremflickr.com/800/600/food,{query.replace(' ', ',')}"
        }])

    except Exception as e:
        print(f"Error detectado: {e}")
        # Respuesta de emergencia profesional
        return jsonify([{
            "title": "Receta no encontrada",
            "kcal": "0", "proteina": "0",
            "ingredients": ["Intenta con otro ingrediente"],
            "instructions": ["Hubo un problema temporal con la IA"],
            "image_url": ""
        }])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)