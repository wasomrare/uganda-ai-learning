import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../config/theme.dart';
import '../../services/api_service.dart';
import '../../models/assessment_model.dart';

final _resultProvider = FutureProvider.family<AttemptResult, String>((ref, attemptId) async {
  final api = ref.read(apiServiceProvider);
  final res = await api.getAttemptResult(attemptId);
  return AttemptResult.fromJson(res.data['data'] as Map<String, dynamic>);
});

class AssessmentResultScreen extends ConsumerWidget {
  final String attemptId;
  const AssessmentResultScreen({super.key, required this.attemptId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final resultAsync = ref.watch(_resultProvider(attemptId));

    return Scaffold(
      backgroundColor: AppColors.background,
      body: resultAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (result) {
          final gradeColor = result.percentage >= 75 ? AppColors.success
              : result.percentage >= 55 ? AppColors.warning
              : AppColors.error;

          return SafeArea(
            child: SingleChildScrollView(
              child: Column(
                children: [
                  // Result header
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(32),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [gradeColor.withOpacity(0.9), gradeColor],
                        begin: Alignment.topLeft, end: Alignment.bottomRight,
                      ),
                    ),
                    child: Column(children: [
                      Text(result.percentage >= 75 ? '🎉' : result.percentage >= 55 ? '👍' : '😔', style: const TextStyle(fontSize: 48)),
                      const SizedBox(height: 12),
                      Text(result.grade, style: const TextStyle(fontSize: 48, fontWeight: FontWeight.bold, color: Colors.white)),
                      Text(result.comment, style: const TextStyle(fontSize: 20, color: Colors.white)),
                      const SizedBox(height: 8),
                      Text('${result.percentage.toStringAsFixed(1)}%', style: TextStyle(fontSize: 16, color: Colors.white.withOpacity(0.9))),
                      Text('${result.score.toStringAsFixed(1)} / ${result.totalMarks} marks', style: TextStyle(fontSize: 14, color: Colors.white.withOpacity(0.8))),
                    ]),
                  ),

                  Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Stats
                        Row(children: [
                          Expanded(child: _StatTile(icon: Icons.check_circle_outline, label: 'Correct', value: '${result.questionResults.where((q) => q.isCorrect).length}', color: AppColors.success)),
                          const SizedBox(width: 12),
                          Expanded(child: _StatTile(icon: Icons.cancel_outlined, label: 'Wrong', value: '${result.questionResults.where((q) => !q.isCorrect).length}', color: AppColors.error)),
                          const SizedBox(width: 12),
                          Expanded(child: _StatTile(icon: Icons.timer_outlined, label: 'Time', value: '${result.timeTaken ~/ 60}m', color: AppColors.secondary)),
                        ]),
                        const SizedBox(height: 24),

                        // Question breakdown
                        Text('Question Breakdown', style: Theme.of(context).textTheme.titleMedium),
                        const SizedBox(height: 12),
                        ...result.questionResults.asMap().entries.map((e) {
                          final i = e.key;
                          final q = e.value;
                          return Container(
                            margin: const EdgeInsets.only(bottom: 8),
                            padding: const EdgeInsets.all(14),
                            decoration: BoxDecoration(
                              color: AppColors.surface,
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: q.isCorrect ? AppColors.success.withOpacity(0.3) : AppColors.error.withOpacity(0.3)),
                            ),
                            child: Row(children: [
                              CircleAvatar(
                                radius: 14,
                                backgroundColor: q.isCorrect ? AppColors.success.withOpacity(0.15) : AppColors.error.withOpacity(0.15),
                                child: Icon(q.isCorrect ? Icons.check : Icons.close, size: 14, color: q.isCorrect ? AppColors.success : AppColors.error),
                              ),
                              const SizedBox(width: 12),
                              Expanded(child: Text('Question ${i + 1}', style: const TextStyle(fontWeight: FontWeight.w500))),
                              Text('${q.marksEarned.toStringAsFixed(1)} marks', style: TextStyle(fontSize: 12, color: q.isCorrect ? AppColors.success : AppColors.error, fontWeight: FontWeight.w600)),
                            ]),
                          );
                        }),

                        const SizedBox(height: 24),
                        Row(children: [
                          Expanded(
                            child: OutlinedButton(
                              onPressed: () => context.go('/home'),
                              child: const Text('Home'),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: () => context.go('/ai-tutor'),
                              icon: const Icon(Icons.smart_toy_outlined, size: 16),
                              label: const Text('Review with AI'),
                            ),
                          ),
                        ]),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class _StatTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;
  const _StatTile({required this.icon, required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: color.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: Column(children: [
        Icon(icon, color: color, size: 24),
        const SizedBox(height: 6),
        Text(value, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: color)),
        Text(label, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
      ]),
    );
  }
}
