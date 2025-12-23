import 'dart:convert';
import 'package:http/http.dart' as http;
import '../data/models/pantry_ingredient.dart';

class PantryService {
  final String baseUrl = 'http://127.0.0.1:8000'; // URL del Backend local

  Future<void> addIngredient(String name, double quantity, String unit, DateTime expirationDate) async {
    final url = Uri.parse('$baseUrl/pantry/add');
    final newIngredient = PantryIngredient(
      ingredientId: '', 
      name: name,
      quantity: quantity,
      unit: unit,
      expirationDate: expirationDate,
    );

    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(newIngredient.toJson()),
    );

    if (response.statusCode != 200) {
      throw Exception('Error al añadir ingrediente: ${response.body}');
    }
  }

  Future<List<PantryIngredient>> listPantry() async {
    final url = Uri.parse('$baseUrl/pantry/list');
    final response = await http.get(url);

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => PantryIngredient.fromJson(json)).toList();
    } else {
      throw Exception('Error al cargar la despensa');
    }
  }
}