// Archivo: recipe_service.dart

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../data/models/recipe.dart';
import '../data/models/ingredient_required.dart'; // Aunque no se usa directamente aquí, es parte del modelo

class RecipeService {
  // URL base de nuestro Backend (asumiremos que está en un servidor local por ahora)
  final String _baseUrl = 'http://localhost:8000/api/v1'; 

  // Simulación de un token de autenticación
  final String _authToken = 'Bearer YOUR_JWT_TOKEN_HERE'; 

  // Método para solicitar una receta a Gemini a través de nuestro Backend
  Future<Recipe> generateRecipe(List<String> ingredients, String userTier) async {
    
    // 1. Construcción de la URL y los encabezados (Headers)
    final url = Uri.parse('$_baseUrl/recipes/generate');
    final headers = {
      'Content-Type': 'application/json',
      'Authorization': _authToken,
    };

    // 2. Creación del cuerpo de la solicitud (Body)
    // Esto coincide con la estructura de la API que definimos en la Fase 1
    final body = jsonEncode({
      'ingredients': ingredients,
      'preferences': {
        'max_time_minutes': 60,
        'difficulty': 'Medio',
        'meal_type': 'Cena',
        'language': 'es',
      },
      'user_tier': userTier,
    });

    try {
      // 3. Llamada HTTP POST al Backend
      final response = await http.post(url, headers: headers, body: body);

      if (response.statusCode == 200) {
        // 4. Éxito: Decodificar la respuesta JSON y crear el objeto Recipe
        final jsonResponse = jsonDecode(utf8.decode(response.bodyBytes));
        return Recipe.fromJson(jsonResponse);

      } else if (response.statusCode == 403) {
        // Manejo de la cuota del nivel Gratuito (ej. QUOTA_EXCEEDED)
        throw Exception("Cuota de recetas excedida para el nivel $userTier. ¡Considera actualizar!");
        
      } else {
        // Otros errores (400, 500, 503)
        print('Error en la API: ${response.statusCode}, Mensaje: ${response.body}');
        throw Exception('Fallo al generar la receta. Inténtalo de nuevo más tarde.');
      }
    } catch (e) {
      // Error de red (ej. servidor no disponible)
      throw Exception('No se pudo conectar con el servidor Sous Chef: $e');
    }
  }
}