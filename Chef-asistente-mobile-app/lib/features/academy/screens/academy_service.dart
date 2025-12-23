// Archivo: academy_test_screen.dart

import 'package:flutter/material.dart';
import '../../../services/academy_service.dart';
import '../../../data/models/academy_content.dart';

class AcademyTestScreen extends StatefulWidget {
  const AcademyTestScreen({super.key});

  @override
  State<AcademyTestScreen> createState() => _AcademyTestScreenState();
}

class _AcademyTestRunnerState extends State<AcademyTestScreen> {
  String testResult = "Presiona el botón para probar la Academia...";

  // La función que contiene la lógica de prueba (Módulo 6)
  void runAcademyTest() async {
    setState(() {
      testResult = '>>> Solicitando contenido a la IA...';
    });
    final academyService = AcademyService();

    try {
      // Usamos el target de ejemplo
      final lesson = await academyService.generateContent(
        'leccion_rapida', 
        'Cómo picar cebolla sin llorar' 
      );
      
      // Si tiene éxito, actualizamos el resultado visible
      setState(() {
        testResult = 
          '✅ ¡ÉXITO! Conexión con Gemini OK.\n'
          'Título: ${lesson.title}\n'
          'Punto Clave 1: ${lesson.keyPoints.first}';
      });
      
    } catch (e) {
      // Si falla, mostramos el error visiblemente
      setState(() {
        testResult = '❌ ¡FALLÓ LA PRUEBA! Error: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Test Módulo 6: Academia')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              // Muestra el resultado de la prueba
              Text(testResult, textAlign: TextAlign.center, style: const TextStyle(fontSize: 16)),
              const SizedBox(height: 40),
              // Botón para ejecutar la prueba
              ElevatedButton(
                onPressed: runAcademyTest, 
                child: const Text('EJECUTAR PRUEBA DE ACADEMIA (Gemini)'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}