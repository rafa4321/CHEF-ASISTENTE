// Archivo: pantry_test_screen.dart

import 'package:flutter/material.dart';
import '../../../services/pantry_service.dart';
import '../../../data/models/pantry_ingredient.dart';

class PantryTestScreen extends StatefulWidget {
  const PantryTestScreen({super.key});

  @override
  State<PantryTestScreen> createState() => _PantryTestScreenState();
}

class _PantryTestScreenState extends State<PantryTestScreen> {
  String testResult = "Presiona el botón para probar la Despensa...";
  List<PantryIngredient> ingredients = [];

  // ----------------------------------------------------
  // La función que ejecuta la prueba de adición y listado
  // ----------------------------------------------------
  void runPantryTest() async {
    setState(() {
      testResult = '>>> Iniciando prueba de la Despensa (Add & List)...';
    });
    final pantryService = PantryService();
    
    // 1. Datos de prueba: Añadir 500g de Cebollas con fecha de caducidad
    final DateTime expiryDate = DateTime.now().add(const Duration(days: 14));
    
    try {
      // 2. Ejecutar la Prueba 1: Añadir Ingrediente
      await pantryService.addIngredient(
        'Cebollas de Prueba', 
        500.0, 
        'gramos', 
        expiryDate
      );
      
      // 3. Ejecutar la Prueba 2: Listar Ingredientes
      final List<PantryIngredient> pantryList = await pantryService.listPantry();
      
      // 4. Verificación: Buscar la cebolla añadida
      final addedIngredient = pantryList.firstWhere(
        (i) => i.name == 'Cebollas de Prueba',
        orElse: () => throw Exception("ERROR: No se encontró la cebolla añadida.")
      );

      // 5. Éxito: Mostrar los resultados
      setState(() {
        testResult = 
          '✅ ¡ÉXITO! Módulo Despensa Operativo.\n'
          'Total de Ingredientes en BD: ${pantryList.length}\n'
          'Ingrediente Añadido: ${addedIngredient.name} (${addedIngredient.quantity} ${addedIngredient.unit})';
        ingredients = pantryList;
      });
      
    } catch (e) {
      // 6. Fallo: Mostrar el error de conexión o de lógica
      setState(() {
        testResult = '❌ ¡FALLÓ LA PRUEBA DE DESPENSA! Error: $e';
        ingredients = [];
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Test Módulo 3: Despensa')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              children: [
                Text(testResult, textAlign: TextAlign.center, style: const TextStyle(fontSize: 16)),
                const SizedBox(height: 20),
                ElevatedButton(
                  onPressed: runPantryTest, 
                  child: const Text('EJECUTAR PRUEBA DE DESPENSA (BD)'),
                ),
              ],
            ),
          ),
          // Muestra la lista de ingredientes si la prueba fue exitosa
          Expanded(
            child: ListView.builder(
              itemCount: ingredients.length,
              itemBuilder: (context, index) {
                final item = ingredients[index];
                final daysUntilExpiry = item.expirationDate.difference(DateTime.now()).inDays;
                final color = daysUntilExpiry <= 3 ? Colors.red : Colors.green;
                
                return ListTile(
                  title: Text(item.name),
                  subtitle: Text('ID: ${item.ingredientId.substring(0, 8)} | Cantidad: ${item.quantity} ${item.unit}'),
                  trailing: Container(
                    padding: const EdgeInsets.all(5),
                    decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(5)),
                    child: Text('$daysUntilExpiry días', style: const TextStyle(color: Colors.white)),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}