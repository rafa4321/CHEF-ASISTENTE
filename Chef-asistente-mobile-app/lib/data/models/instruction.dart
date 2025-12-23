// Archivo: instruction.dart

class Instruction {
  final int stepNumber;
  final String description;
  final int timerMinutes; // Tiempo del temporizador para el Chef al Oído

  Instruction({
    required this.stepNumber,
    required this.description,
    required this.timerMinutes,
  });

  // Constructor para crear un objeto Instruction a partir de un mapa JSON
  factory Instruction.fromJson(Map<String, dynamic> json) {
    return Instruction(
      stepNumber: json['step_number'] as int,
      description: json['description'] as String,
      timerMinutes: json['timer_minutes'] as int,
    );
  }
}