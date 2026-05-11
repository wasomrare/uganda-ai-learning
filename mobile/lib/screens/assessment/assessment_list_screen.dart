import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../config/theme.dart';
import '../../services/api_service.dart';

final _assessmentsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final api = ref.read(apiServiceProvider);
  final res = await api.getMyAssessments(params: {'status': 'active'});
  final data = res.data['data'];
  if (data is Map && data.containsKey('results')) {
    return List<Map<String, dynamic>>.from(data['results'] as List);
  }
  return List<Map<String, dynamic>>.from(data as List? ?? []);
});

class AssessmentListScreen extends ConsumerWidget {
  const AssessmentListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final assessmentsAsync = ref.watch(_assessmentsProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(title: const Text('Assessments')),
      body: assessmentsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (assessments) => assessments.isEmpty
            ? Center(
                child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                  const Icon(Icons.quiz_outlined, size: 64, color: AppColors.textHint),
                  const SizedBox(height: 12),
                  const Text('No active assessments', style: TextStyle(color: AppColors.textSecondary, fontSize: 16)),
                  const SizedBox(height: 8),
                  const Text('Check back later for new tests', style: TextStyle(color: AppColors.textHint)),
                ]),
              )
            : ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: assessments.length,
                separatorBuilder: (_, __) => const SizedBox(height: 10),
                itemBuilder: (context, index) {
                  final a = assessments[index];
                  return _AssessmentCard(data: a, onTap: () => context.push('/assessments/${a['id']}'));
                },
              ),
      ),
    );
  }
}

class _AssessmentCard extends StatelessWidget {
  final Map<String, dynamic> data;
  final VoidCallback onTap;
  const _AssessmentCard({required this.data, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final typeColors = {
      'weekly_quiz': AppColors.secondary,
      'monthly_test': AppColors.accent,
      'end_of_term': AppColors.error,
      'diagnostic': const Color(0xFF8B5CF6),
    };
    final color = typeColors[data['assessment_type']] ?? AppColors.primary;
    final typeLabel = {
      'weekly_quiz': 'Weekly Quiz',
      'monthly_test': 'Monthly Test',
      'end_of_term': 'End of Term',
      'diagnostic': 'Diagnostic',
      'holiday_revision': 'Holiday',
      'custom': 'Custom',
    }[data['assessment_type']] ?? 'Test';

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.border),
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 8, offset: const Offset(0, 2))],
        ),
        child: Row(
          children: [
            Container(
              width: 48, height: 48,
              decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(12)),
              child: Icon(Icons.quiz_rounded, color: color, size: 24),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(data['title'] as String? ?? '', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15)),
                  const SizedBox(height: 4),
                  Wrap(
                    spacing: 6,
                    children: [
                      _Pill(text: typeLabel, color: color),
                      _Pill(text: '${data['duration_minutes']} min', color: AppColors.textSecondary),
                      _Pill(text: '${data['question_count']} Qs', color: AppColors.textSecondary),
                      _Pill(text: '${data['total_marks']} marks', color: AppColors.textSecondary),
                    ],
                  ),
                ],
              ),
            ),
            Icon(Icons.arrow_forward_ios, size: 14, color: AppColors.textHint),
          ],
        ),
      ),
    );
  }
}

class _Pill extends StatelessWidget {
  final String text;
  final Color color;
  const _Pill({required this.text, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(20)),
      child: Text(text, style: TextStyle(fontSize: 10, color: color, fontWeight: FontWeight.w500)),
    );
  }
}
