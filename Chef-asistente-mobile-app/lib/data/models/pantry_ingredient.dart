class PantryIngredient {
  final String ingredientId;
  final String name;
  final double quantity;
  final String unit;
  final DateTime expirationDate;

  PantryIngredient({
    required this.ingredientId,
    required this.name,
    required this.quantity,
    required this.unit,
    required this.expirationDate,
  });

  factory PantryIngredient.fromJson(Map<String, dynamic> json) {
    return PantryIngredient(
      ingredientId: json['id'] ?? '',
      name: json['name'] ?? 'Desconocido',
      quantity: (json['quantity'] as num).toDouble(),
      unit: json['unit'] ?? '',
      expirationDate: DateTime.parse(json['expiration_date']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'quantity': quantity,
      'unit': unit,
      'expiration_date': expirationDate.toIso8601String(),
    };
  }
}