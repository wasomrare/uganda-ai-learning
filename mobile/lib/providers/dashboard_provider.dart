import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';

final studentDashboardProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final api = ref.read(apiServiceProvider);
  final res = await api.getStudentDashboard();
  return (res.data['data'] as Map<String, dynamic>?) ?? {};
});

final teacherDashboardProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final api = ref.read(apiServiceProvider);
  final res = await api.getTeacherDashboard();
  return (res.data['data'] as Map<String, dynamic>?) ?? {};
});
