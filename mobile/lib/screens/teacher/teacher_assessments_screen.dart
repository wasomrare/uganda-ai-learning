import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../config/theme.dart';
import '../../services/api_service.dart';

final _teacherAssessmentsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final api = ref.read(apiServiceProvider);
  final res = await api.getMyAssessments();
  final data = res.data['data'];
  if (data is Map && data.containsKey('results')) {
    return List<Map<String, dynamic>>.from(data['results'] as List);
  }
  return List<Map<String, dynamic>>.from(data as List? ?? []);
});

class TeacherAssessmentsScreen extends ConsumerWidget {
  const TeacherAssessmentsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final assessmentsAsync = ref.watch(_teacherAssessmentsProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('My Assessments'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_circle_outline),
            onPressed: () => ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Create assessment coming soon')),
            ),
          ),
        ],
      ),
      body: assessmentsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (assessments) => assessments.isEmpty
            ? const Center(child: Text('No assessments created yet.', style: TextStyle(color: AppColors.textSecondary)))
            : ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: assessments.length,
                itemBuilder: (context, i) {
                  final a = assessments[i];
                  final statusColors = {'draft': Colors.grey, 'active': AppColors.success, 'closed': AppColors.error};
                  final color = statusColors[a['status']] ?? Colors.grey;
                  return Container(
                    margin: const EdgeInsets.only(bottom: 10),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppColors.surface,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: AppColors.border),
                    ),
                    child: Row(children: [
                      Container(
                        width: 44, height: 44,
                        decoration: BoxDecoration(color: AppColors.primary.withOpacity(0.1), borderRadius: BorderRadius.circular(12)),
                        child: const Icon(Icons.quiz_outlined, color: AppColors.primary),
                      ),
                      const SizedBox(width: 12),
                      Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                        Text(a['title'] as String? ?? '', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                        const SizedBox(height: 4),
                        Text('${a['class_level'] ?? ''} · ${a['question_count'] ?? 0} questions · ${a['total_marks'] ?? 0} marks',
                          style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                        if (a['attempt_count'] != null) Text('${a['attempt_count']} attempts · avg ${(a['average_score'] ?? 0).toStringAsFixed(0)}%',
                          style: const TextStyle(fontSize: 11, color: AppColors.textHint)),
                      ])),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(8)),
                        child: Text(a['status'] as String? ?? '', style: TextStyle(fontSize: 10, color: color, fontWeight: FontWeight.w600)),
                      ),
                    ]),
                  );
                },
              ),
      ),
    );
  }
}
