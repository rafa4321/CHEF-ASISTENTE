// Archivo: recipe.dart

import 'instruction.dart';
import 'ingredient_required.dart';

class Recipe {
  final String recipeId;
  final String name;
  final int totalTimeMinutes;
  final String difficulty;
  final int estimatedCalories;
  final String chefTip;
  
  // Lista de objetos Instruction (pasos)
  final List<Instruction> instructions; 
  
  // Lista de objetos IngredientRequired (ingredientes necesarios)
  final List<IngredientRequired> ingredientsList; 

  Recipe({
    required this.recipeId,
    required this.name,
    required this.totalTimeMinutes,
    required this.difficulty,
    required this.estimatedCalories,
    required this.chefTip,
    required this.instructions,
    required this.ingredientsList,
  });

  // Constructor de fábrica para convertir el JSON completo del Backend
  factory Recipe.fromJson(Map<String, dynamic> json) {
    // Mapeo de listas anidadas
    var instructionsList = json['instructions'] as List;
    List<Instruction> instructions = instructionsList.map((i) => Instruction.fromJson(i as Map<String, dynamic>)).toList();

    var ingredientsJsonList = json['ingredients_list'] as List;
    List<IngredientRequired> ingredients = ingredientsJsonList.map((i) => IngredientRequired.fromJson(i as Map<String, dynamic>)).toList();
    
    // Cálculo de tiempo total
    final prepTime = json['prep_time_minutes'] as int? ?? 0;
    final cookTime = json['cook_time_minutes'] as int? ?? 0;

    return Recipe(
      recipeId: json['recipe_id'] as String,
      name: json['name'] as String,
      totalTimeMinutes: prepTime + cookTime, // Sumamos la preparación y cocción
      difficulty: json['difficulty'] as String,
      estimatedCalories: json['estimated_calories'] as int,
      chefTip: json['chef_tip'] as String,
      instructions: instructions,
      ingredientsList: ingredients,
    );
  }
}