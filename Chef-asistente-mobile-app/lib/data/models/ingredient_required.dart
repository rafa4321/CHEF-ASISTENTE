// Archivo: ingredient_required.dart

class IngredientRequired {
  final String name;
  final String quantity; // String para manejar cantidades no numéricas (ej. "al gusto")
  final String unit;

  IngredientRequired({
    required this.name,
    required this.quantity,
    required this.unit,
  });

  // Constructor para crear un objeto IngredientRequired a partir de un mapa JSON
  factory IngredientRequired.fromJson(Map<String, dynamic> json) {
    return IngredientRequired(
      name: json['name'] as String,
      quantity: json['quantity'] as String,
      unit: json['unit'] as String,
    );
  }
}