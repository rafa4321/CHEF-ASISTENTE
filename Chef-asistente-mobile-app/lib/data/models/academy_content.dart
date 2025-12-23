// Archivo: academy_content.dart (Recuerda crear este archivo)

class AcademyContent {
  final String contentId;
  final String title;
  final String contentType;
  final List<String> keyPoints; // Los 3 puntos clave de la lección
  final String expertTip;

  // Constructor que convierte el JSON en un objeto Dart
  AcademyContent.fromJson(Map<String, dynamic> json)
      : contentId = json['content_id'] as String,
        title = json['title'] as String,
        contentType = json['content_type'] as String,
        keyPoints = List<String>.from(json['key_points'] as List),
        expertTip = json['expert_tip'] as String;
}