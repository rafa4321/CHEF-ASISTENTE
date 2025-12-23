// Chef-asistente-mobile-app/lib/services/api_service.dart

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:async'; 

// 🎯 CAMBIO DE IP CRÍTICO: Usamos 10.0.2.2 para el Emulador de Android.
const String BASE_URL = 'http://127.0.0.1:9000'; 


// 1. Estructura de datos para la respuesta de la IA
class RecipeResult {
  final String title;
  final String description;
  final List<String> recommendations;
  final String prepTime; 

  RecipeResult({
    required this.title, 
    required this.description, 
    required this.recommendations, 
    required this.prepTime,
  });

  factory RecipeResult.fromJson(Map<String, dynamic> json) {
    return RecipeResult(
      title: json['title'] as String,
      description: json['description'] as String,
      prepTime: json['prep_time'] as String? ?? 'N/A', 
      recommendations: List<String>.from(json['recommendations'] as List? ?? []),
    );
  }
}

/// Función para buscar recetas (GET /search)
Future<List<RecipeResult>> searchRecipes(String query) async {
  
  final encodedQuery = Uri.encodeComponent(query);
  final url = Uri.parse('$BASE_URL/search?query=$encodedQuery'); 

  try {
    final response = await http.get(
      url,
      headers: {
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> dataList = json.decode(response.body);
      return dataList.map((data) => RecipeResult.fromJson(data)).toList();
    } else {
      // Si el servidor devuelve un error (ej. 500 por fallo de IA)
      final errorData = json.decode(response.body);
      throw Exception(errorData['detail'] ?? 'Error desconocido del servidor (${response.statusCode})');
    }
  } catch (e) {
    // Error de red o la excepción lanzada anteriormente
    throw Exception('Fallo de conexión: $e');
  }
}

// ... (checkBackendConnection permanece igual) ...