// Archivo: menu_service.dart

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../data/models/menu_plan.dart'; // ¡Necesitas crear este molde primero!

class MenuService {
  final String _baseUrl = 'http://localhost:8000/api/v1'; 
  final String _authToken = 'Bearer YOUR_JWT_TOKEN_HERE'; 

  // Método para solicitar la generación del menú semanal al Backend
  Future<MenuPlan> generateWeeklyMenu(String userTier, String planType) async {
    
    // 1. Construcción de la URL y los encabezados
    final url = Uri.parse('$_baseUrl/menus/generate');
    final headers = {
      'Content-Type': 'application/json',
      'Authorization': _authToken,
    };

    // 2. Creación del cuerpo de la solicitud (Parámetros para Gemini)
    final body = jsonEncode({
      'days_to_cover': 7,
      'restrictions': 'Bajo en carbohidratos, sin nueces',
      'budget_limit': 100.00, // Sólo relevante para Nivel Profesional
      'plan_type': planType, // Ej: "Económico" o "Balanceado"
      'user_tier': userTier,
    });

    try {
      // 3. Llamada HTTP POST
      final response = await http.post(url, headers: headers, body: body);

      if (response.statusCode == 200) {
        // 4. Éxito: Decodificar la respuesta JSON y crear el objeto MenuPlan
        final jsonResponse = jsonDecode(utf8.decode(response.bodyBytes));
        return MenuPlan.fromJson(jsonResponse); // Usamos el molde MenuPlan

      } else {
        print('Error en la API: ${response.statusCode}, Mensaje: ${response.body}');
        throw Exception('Fallo al generar el menú semanal. Verifica el Nivel Pro.');
      }
    } catch (e) {
      throw Exception('No se pudo conectar con el servidor Sous Chef: $e');
    }
  }
}