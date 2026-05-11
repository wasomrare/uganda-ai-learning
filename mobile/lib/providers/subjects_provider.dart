import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';

final subjectsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final api = ref.read(apiServiceProvider);
  final res = await api.getSubjects();
  final data = res.data['data'];
  if (data is Map && data.containsKey('results')) {
    return List<Map<String, dynamic>>.from(data['results'] as List);
  }
  return List<Map<String, dynamic>>.from(data as List? ?? []);
});
