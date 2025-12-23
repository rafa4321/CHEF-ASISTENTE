// Chef-asistente-mobile-app/lib/main.dart

import 'package:flutter/material.dart';
import 'services/api_service.dart'; 

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Chef Asistente IA',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepOrange), 
        useMaterial3: true,
        appBarTheme: const AppBarTheme(
          centerTitle: true,
          backgroundColor: Colors.deepOrange, 
          foregroundColor: Colors.white,
          elevation: 4,
        ),
      ),
      home: const RecipeSearchScreen(),
    );
  }
}

class RecipeSearchScreen extends StatefulWidget {
  const RecipeSearchScreen({super.key});

  @override
  State<RecipeSearchScreen> createState() => _RecipeSearchScreenState();
}

class _RecipeSearchScreenState extends State<RecipeSearchScreen> {
  final TextEditingController _searchController = TextEditingController();
  List<RecipeResult> _searchResults = []; 
  String _statusMessage = "Escribe un ingrediente o plato (ej. 'pollo frito') y busca.";
  bool _isLoading = false;

  void _submitSearch() async {
    final String query = _searchController.text.trim();

    if (query.isEmpty) {
      setState(() {
        _statusMessage = "❌ Error: El campo de búsqueda no puede estar vacío.";
        _searchResults = [];
      });
      return;
    }
    
    setState(() {
      _isLoading = true;
      _statusMessage = "Buscando recetas de IA para '$query'...";
      _searchResults = [];
    });

    try {
      final results = await searchRecipes(query); 

      // Éxito
      setState(() {
        _isLoading = false;
        _searchResults = results;
        if (results.isEmpty) {
          _statusMessage = "No se encontraron resultados de la IA para '$query'.";
        } else {
          _statusMessage = "✅ Se encontraron ${results.length} resultados de la IA.";
        }
      });
    } catch (e) {
      // Captura el error exacto (incluyendo fallos de Gemini o clave)
      setState(() {
        _isLoading = false;
        _statusMessage = "❌ Error en la Búsqueda: ${e.toString().replaceFirst('Exception: ', '')}";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Chef Asistente IA (Búsqueda)"),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: <Widget>[
            // Campo de Búsqueda
            TextField(
              controller: _searchController,
              decoration: InputDecoration(
                labelText: 'Ingrediente/Plato a Buscar',
                border: const OutlineInputBorder(
                  borderRadius: BorderRadius.all(Radius.circular(12)),
                ),
                suffixIcon: _isLoading 
                    ? const Padding(padding: EdgeInsets.all(8.0), child: SizedBox(height: 20, width: 20, child: CircularProgressIndicator()))
                    : IconButton(
                        icon: const Icon(Icons.search, color: Colors.deepOrange),
                        onPressed: _submitSearch,
                      ),
              ),
              onSubmitted: (_) => _submitSearch(), 
            ),
            const SizedBox(height: 10),
            // Mensaje de Estado
            Text(
              _statusMessage,
              style: TextStyle(
                fontSize: 14,
                color: _statusMessage.startsWith("❌") ? Colors.red : Colors.deepOrange.shade700,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 20),
            // Resultados en Lista
            Expanded(
              child: ListView.builder(
                itemCount: _searchResults.length,
                itemBuilder: (context, index) {
                  final recipe = _searchResults[index];
                  
                  // Diseño de la tarjeta (ExpansionTile con iconos)
                  return Card(
                    margin: const EdgeInsets.only(bottom: 15),
                    elevation: 6, 
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    child: ExpansionTile(
                      leading: const Icon(Icons.restaurant_menu, color: Colors.deepOrange, size: 30), 
                      title: Text(
                        recipe.title, 
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                      ),
                      subtitle: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(recipe.description, maxLines: 2, overflow: TextOverflow.ellipsis),
                          const SizedBox(height: 5),
                          Row(
                            children: [
                              const Icon(Icons.timer, size: 16, color: Colors.grey),
                              const SizedBox(width: 4),
                              Text(recipe.prepTime, style: TextStyle(fontSize: 12, color: Colors.grey)),
                            ],
                          ),
                        ],
                      ),
                      children: <Widget>[
                        Padding(
                          padding: const EdgeInsets.all(16.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                "Consejos de IA y Recomendaciones:", 
                                style: TextStyle(fontWeight: FontWeight.bold, color: Colors.deepOrange),
                              ),
                              const SizedBox(height: 8),
                              ...recipe.recommendations.map((rec) => Padding(
                                padding: const EdgeInsets.only(left: 8.0, top: 4.0),
                                child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Icon(Icons.lightbulb_outline, size: 16, color: Colors.amber),
                                    const SizedBox(width: 8),
                                    Expanded(child: Text(rec)),
                                  ],
                                ),
                              )).toList(),
                            ],
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}