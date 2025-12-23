import 'dart:convert';
import 'package:http/http.dart' as http;

// 🎯 CONFIGURACIÓN IP:
// Web (Chrome): Usa 'http://127.0.0.1:9000'
// Android Emulator: Usa 'http://10.0.2.2:9000'

// ✅ CORRECCIÓN APLICADA: URL limpia sin corchetes ni paréntesis
const String BASE_URL = 'http://127.0.0.1:9000';

class RecipeResult {
  final String title;
  final String description;
  final List<String> ingredients;
  final List<String> instructions;
  final String prepTime;
  final String calories;
  final Map<String, dynamic> macros;
  final String estimatedPrice;
  final String dietType;
  final String nutritionalNotes;

  RecipeResult({
    required this.title,
    required this.description,
    required this.ingredients,
    required this.instructions,
    required this.prepTime,
    required this.calories,
    required this.macros,
    required this.estimatedPrice,
    required this.dietType,
    required this.nutritionalNotes,
  });

  factory RecipeResult.fromJson(Map<String, dynamic> json) {
    return RecipeResult(
      title: json['title'] ?? 'Sin título',
      description: json['description'] ?? '',
      ingredients: List<String>.from(json['ingredients'] ?? []),
      instructions: List<String>.from(json['instructions'] ?? []),
      prepTime: json['prep_time'] ?? 'N/A',
      calories: json['calories'] ?? 'N/A',
      macros: Map<String, dynamic>.from(json['macros'] ?? {}),
      estimatedPrice: json['estimated_price'] ?? 'N/A',
      dietType: json['diet_type'] ?? 'General',
      nutritionalNotes: json['nutritional_notes'] ?? '',
    );
  }
}

Future<List<RecipeResult>> searchRecipes(String query) async {
  // Construcción segura de la URL
  final url = Uri.parse('$BASE_URL/search?query=${Uri.encodeComponent(query)}');
  
  try {
    final response = await http.get(url);
    
    if (response.statusCode == 200) {
      // Decodificar respuesta UTF-8 para evitar problemas con tildes/eñes
      final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
      return data.map((d) => RecipeResult.fromJson(d)).toList();
    } else {
      throw Exception('Error servidor: ${response.statusCode}');
    }
  } catch (e) {
    throw Exception('Error conexión: $e');
  }
}