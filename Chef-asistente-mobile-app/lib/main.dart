import 'package:flutter/material.dart';
import 'services/api_service.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(useMaterial3: true, colorSchemeSeed: Colors.green),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _ctrl = TextEditingController();
  List<RecipeResult> _recipes = [];
  bool _loading = false;

  void _search() async {
    if (_ctrl.text.isEmpty) return;
    setState(() => _loading = true);
    try {
      final res = await searchRecipes(_ctrl.text);
      setState(() => _recipes = res);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("🍳 Chef & Nutricionista AI"), centerTitle: true),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _ctrl,
              decoration: InputDecoration(
                hintText: "Ej: Cena Keto de \$10, 500 cal",
                suffixIcon: IconButton(onPressed: _search, icon: const Icon(Icons.send)),
                border: const OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(12))),
              ),
              onSubmitted: (_) => _search(),
            ),
          ),
          if (_loading) const LinearProgressIndicator(),
          Expanded(
            child: ListView.builder(
              itemCount: _recipes.length,
              itemBuilder: (c, i) => RecipeCard(recipe: _recipes[i]),
            ),
          ),
        ],
      ),
    );
  }
}

class RecipeCard extends StatelessWidget {
  final RecipeResult recipe;
  const RecipeCard({super.key, required this.recipe});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(12),
      elevation: 4,
      child: ExpansionTile(
        leading: const Icon(Icons.restaurant_menu, color: Colors.green),
        title: Text(recipe.title, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text("${recipe.calories} | ${recipe.estimatedPrice}"),
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("Dieta: ${recipe.dietType}", style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.green)),
                const SizedBox(height: 8),
                Text(recipe.description, style: const TextStyle(fontStyle: FontStyle.italic)),
                const Divider(),
                _header("Ingredientes & Costos"),
                ...recipe.ingredients.map((e) => Text("• $e")),
                const SizedBox(height: 10),
                _header("Instrucciones"),
                ...recipe.instructions.map((e) => Text("- $e")),
                const Divider(),
                _header("Nutrición"),
                Text("Macros: ${recipe.macros}"),
                Text("Notas: ${recipe.nutritionalNotes}"),
              ],
            ),
          )
        ],
      ),
    );
  }
  Widget _header(String t) => Text(t, style: const TextStyle(fontWeight: FontWeight.bold));
}