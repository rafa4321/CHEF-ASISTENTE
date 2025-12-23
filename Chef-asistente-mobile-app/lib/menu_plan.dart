// Archivo: menu_plan.dart

class MenuItem {
  final String mealType; // Ej: "Almuerzo", "Cena"
  final String recipeName; 
  final String recipeId;
  final double estimatedCost; // Clave para el Nivel Profesional

  MenuItem.fromJson(Map<String, dynamic> json)
      : mealType = json['meal_type'],
        recipeName = json['recipe_name'],
        recipeId = json['recipe_id'],
        estimatedCost = (json['estimated_cost'] as num).toDouble();
}

class MenuDay {
  final String dayName; // Ej: "Lunes"
  final List<MenuItem> meals;

  MenuDay.fromJson(Map<String, dynamic> json)
      : dayName = json['day_name'],
        meals = (json['meals'] as List)
            .map((i) => MenuItem.fromJson(i as Map<String, dynamic>))
            .toList();
}

class MenuPlan {
  final String menuId;
  final double totalEstimatedCost;
  final List<MenuDay> dailyMeals;
  // Nota: La 'shopping_list' se incluiría aquí también.

  MenuPlan.fromJson(Map<String, dynamic> json)
      : menuId = json['menu_id'],
        totalEstimatedCost = (json['total_estimated_cost'] as num).toDouble(),
        dailyMeals = (json['daily_meals'] as List)
            .map((i) => MenuDay.fromJson(i as Map<String, dynamic>))
            .toList();
}