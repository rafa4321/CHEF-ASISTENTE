// Archivo: vision_service.dart

import 'dart:io'; // Para manejar archivos de imagen
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../data/models/recipe.dart'; 

class VisionService {
  final String _baseUrl = 'http://localhost:8000/api/v1'; 
  final String _authToken = 'Bearer YOUR_JWT_TOKEN_HERE'; 

  Future<Recipe> analyzePantryImage(File imageFile, String userTier) async {
    final url = Uri.parse('$_baseUrl/recipes/analyze-image');
    
    // 1. Crear una solicitud multipart para enviar el archivo
    var request = http.MultipartRequest('POST', url)
      ..headers['Authorization'] = _authToken
      ..fields['user_tier'] = userTier; // Parámetros adicionales

    // 2. Adjuntar la imagen al cuerpo de la solicitud
    request.files.add(await http.MultipartFile.fromPath(
      'pantry_image', // Este debe ser el nombre del campo esperado por el Backend
      imageFile.path,
    ));

    // 3. Enviar la solicitud
    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      // Éxito: El Backend (Gemini) envió una receta
      final jsonResponse = jsonDecode(utf8.decode(response.bodyBytes));
      return Recipe.fromJson(jsonResponse); // Usamos el molde de Receta que ya creaste

    } else {
      // Manejo de errores (ej. Gemini no pudo identificar nada)
      throw Exception('Fallo en el análisis de imagen. Código: ${response.statusCode}');
    }
  }
}