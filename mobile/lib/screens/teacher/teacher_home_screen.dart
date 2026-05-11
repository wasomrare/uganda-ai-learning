import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../config/theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/dashboard_provider.dart';
import '../../widgets/stat_card.dart';

class TeacherHomeScreen extends ConsumerWidget {
  const TeacherHomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authStateProvider).valueOrNull?.user;
    final dashboard = ref.watch(teacherDashboardProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        automaticallyImplyLeading: false,
        title: Row(children: [
          CircleAvatar(
            radius: 16,
            backgroundColor: AppColors.primaryLight,
            child: Text(user?.initials ?? 'T', style: const TextStyle(color: AppColors.primary, fontSize: 13, fontWeight: FontWeight.bold)),
          ),
          const SizedBox(width: 10),
          Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text('${user?.fullName ?? 'Teacher'}', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
            const Text('Teacher Dashboard', style: TextStyle(fontSize: 11, color: AppColors.textSecondary)),
          ]),
        ]),
        actions: [
          IconButton(icon: const Icon(Icons.notifications_outlined), onPressed: () {}),
          PopupMenuButton<String>(
            onSelected: (v) async {
              if (v == 'logout') {
                await ref.read(authStateProvider.notifier).logout();
                if (context.mounted) context.go('/login');
              }
            },
            itemBuilder: (_) => [
              const PopupMenuItem(value: 'profile', child: Text('Profile')),
              const PopupMenuItem(value: 'logout', child: Text('Logout')),
            ],
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Stats
            dashboard.when(
              loading: () => const SizedBox(height: 80, child: Center(child: CircularProgressIndicator())),
              error: (e, _) => Text('Dashboard error: $e'),
              data: (data) => Column(children: [
                Row(children: [
                  Expanded(child: StatCard(label: 'Students', value: '${data['total_students'] ?? 0}', icon: Icons.people_outlined, color: AppColors.secondary)),
                  const SizedBox(width: 10),
                  Expanded(child: StatCard(label: 'Classes', value: '${data['total_classes'] ?? 0}', icon: Icons.class_outlined, color: AppColors.primary)),
                ]),
                const SizedBox(height: 10),
                Row(children: [
                  Expanded(child: StatCard(label: 'Assessments', value: '${data['total_assessments'] ?? 0}', icon: Icons.quiz_outlined, color: AppColors.accent)),
                  const SizedBox(width: 10),
                  Expanded(child: StatCard(label: 'Avg Score', value: '${(data['average_score'] ?? 0).toStringAsFixed(0)}%', icon: Icons.bar_chart, color: AppColors.success)),
                ]),
              ]),
            ),
            const SizedBox(height: 24),

            Text('Quick Actions', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            _Grid(children: [
              _ActionCard(icon: Icons.quiz_rounded, label: 'My Assessments', color: AppColors.secondary, onTap: () => context.push('/teacher/assessments')),
              _ActionCard(icon: Icons.smart_toy_rounded, label: 'AI Questions', color: AppColors.accent, onTap: () {}),
              _ActionCard(icon: Icons.people_rounded, label: 'My Students', color: AppColors.primary, onTap: () {}),
              _ActionCard(icon: Icons.analytics_rounded, label: 'Reports', color: AppColors.error, onTap: () {}),
              _ActionCard(icon: Icons.video_call_rounded, label: 'Live Class', color: const Color(0xFF8B5CF6), onTap: () {}),
              _ActionCard(icon: Icons.upload_file_rounded, label: 'Upload Notes', color: const Color(0xFF06B6D4), onTap: () {}),
            ]),
          ],
        ),
      ),
    );
  }
}

class _Grid extends StatelessWidget {
  final List<Widget> children;
  const _Grid({required this.children});

  @override
  Widget build(BuildContext context) => GridView.count(
    shrinkWrap: true, physics: const NeverScrollableScrollPhysics(),
    crossAxisCount: 3, childAspectRatio: 0.85, crossAxisSpacing: 10, mainAxisSpacing: 10,
    children: children,
  );
}

class _ActionCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;
  const _ActionCard({required this.icon, required this.label, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: color.withOpacity(0.08),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: color.withOpacity(0.15)),
        ),
        child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: color.withOpacity(0.12), shape: BoxShape.circle),
            child: Icon(icon, color: color, size: 22),
          ),
          const SizedBox(height: 8),
          Text(label, textAlign: TextAlign.center, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: color.withOpacity(0.9)), maxLines: 2),
        ]),
      ),
    );
  }
}
