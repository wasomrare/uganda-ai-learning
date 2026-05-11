import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../config/theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/dashboard_provider.dart';
import '../../widgets/stat_card.dart';
import '../../widgets/subject_chip.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authStateProvider).valueOrNull;
    final dashboard = ref.watch(studentDashboardProvider);
    final user = authState?.user;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            SliverToBoxAdapter(
              child: Container(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 24),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [AppColors.primary, AppColors.primaryDark],
                    begin: Alignment.topLeft, end: Alignment.bottomRight,
                  ),
                  borderRadius: const BorderRadius.vertical(bottom: Radius.circular(28)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                          Text('Hello, ${user?.firstName ?? 'Learner'}! 👋',
                            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white)),
                          const SizedBox(height: 4),
                          Text('Keep learning today!',
                            style: TextStyle(fontSize: 13, color: Colors.white.withOpacity(0.8))),
                        ]),
                        GestureDetector(
                          onTap: () => context.push('/notifications'),
                          child: Stack(children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(color: Colors.white.withOpacity(0.2), borderRadius: BorderRadius.circular(12)),
                              child: const Icon(Icons.notifications_outlined, color: Colors.white, size: 22),
                            ),
                            Positioned(
                              top: 4, right: 4,
                              child: Container(width: 8, height: 8, decoration: const BoxDecoration(color: AppColors.ugandaYellow, shape: BoxShape.circle)),
                            ),
                          ]),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    // XP Bar
                    dashboard.when(
                      data: (data) => _XpBar(xp: data['xp'] ?? 0, level: data['level'] ?? 1),
                      loading: () => const _XpBarSkeleton(),
                      error: (_, __) => const _XpBarSkeleton(),
                    ),
                  ],
                ),
              ),
            ),

            SliverPadding(
              padding: const EdgeInsets.all(16),
              sliver: SliverToBoxAdapter(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Stats
                    dashboard.when(
                      data: (data) => _StatsRow(data: data),
                      loading: () => const _StatsRowSkeleton(),
                      error: (_, __) => const _StatsRowSkeleton(),
                    ),
                    const SizedBox(height: 20),

                    // Quick Actions
                    Text('Quick Actions', style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 12),
                    GridView.count(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      crossAxisCount: 2, mainAxisSpacing: 12, crossAxisSpacing: 12, childAspectRatio: 1.8,
                      children: [
                        _ActionCard(icon: Icons.quiz_rounded, label: 'Take Test', color: AppColors.secondary, onTap: () => context.go('/assessments')),
                        _ActionCard(icon: Icons.smart_toy_rounded, label: 'Ask AI', color: AppColors.accent, onTap: () => context.go('/ai-tutor')),
                        _ActionCard(icon: Icons.replay_rounded, label: 'Revision', color: AppColors.primary, onTap: () => context.push('/revision')),
                        _ActionCard(icon: Icons.leaderboard_rounded, label: 'Rankings', color: AppColors.error, onTap: () => context.push('/leaderboard')),
                      ],
                    ),
                    const SizedBox(height: 20),

                    // Subjects
                    Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
                      Text('Subjects', style: Theme.of(context).textTheme.titleMedium),
                      TextButton(onPressed: () => context.go('/subjects'), child: const Text('See all')),
                    ]),
                    const SizedBox(height: 10),
                    SizedBox(
                      height: 44,
                      child: ListView(
                        scrollDirection: Axis.horizontal,
                        children: const ['Math', 'English', 'Science', 'SST', 'Luganda', 'CRE']
                            .map((s) => Padding(
                              padding: const EdgeInsets.only(right: 8),
                              child: SubjectChip(label: s),
                            ))
                            .toList(),
                      ),
                    ),
                    const SizedBox(height: 20),

                    // Streak
                    dashboard.when(
                      data: (data) => _StreakCard(streak: data['streak'] ?? 0, maxStreak: data['max_streak'] ?? 0),
                      loading: () => const SizedBox.shrink(),
                      error: (_, __) => const SizedBox.shrink(),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _XpBar extends StatelessWidget {
  final int xp;
  final int level;
  const _XpBar({required this.xp, required this.level});

  @override
  Widget build(BuildContext context) {
    final progress = (xp % 500) / 500;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
          Text('Level $level', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 13)),
          Text('$xp XP', style: TextStyle(color: Colors.white.withOpacity(0.8), fontSize: 12)),
        ]),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(10),
          child: LinearProgressIndicator(
            value: progress.clamp(0.0, 1.0),
            backgroundColor: Colors.white.withOpacity(0.2),
            valueColor: const AlwaysStoppedAnimation(AppColors.ugandaYellow),
            minHeight: 8,
          ),
        ),
      ],
    );
  }
}

class _XpBarSkeleton extends StatelessWidget {
  const _XpBarSkeleton();
  @override
  Widget build(BuildContext context) {
    return Container(height: 30, decoration: BoxDecoration(color: Colors.white.withOpacity(0.2), borderRadius: BorderRadius.circular(8)));
  }
}

class _StatsRow extends StatelessWidget {
  final Map<String, dynamic> data;
  const _StatsRow({required this.data});
  @override
  Widget build(BuildContext context) {
    return Row(children: [
      Expanded(child: StatCard(label: 'Tests Done', value: '${data['total_attempts'] ?? 0}', icon: Icons.quiz_outlined, color: AppColors.secondary)),
      const SizedBox(width: 10),
      Expanded(child: StatCard(label: 'Avg Score', value: '${(data['average_score'] ?? 0).toStringAsFixed(0)}%', icon: Icons.bar_chart, color: AppColors.primary)),
      const SizedBox(width: 10),
      Expanded(child: StatCard(label: 'Badges', value: '${data['badges_count'] ?? 0}', icon: Icons.military_tech_outlined, color: AppColors.accent)),
    ]);
  }
}

class _StatsRowSkeleton extends StatelessWidget {
  const _StatsRowSkeleton();
  @override
  Widget build(BuildContext context) {
    return Row(children: List.generate(3, (i) =>
      Expanded(child: Container(height: 72, margin: EdgeInsets.only(right: i < 2 ? 10 : 0), decoration: BoxDecoration(color: Colors.grey[200], borderRadius: BorderRadius.circular(14))))));
  }
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
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: color.withOpacity(0.2)),
        ),
        padding: const EdgeInsets.all(14),
        child: Row(children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(color: color.withOpacity(0.15), borderRadius: BorderRadius.circular(10)),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 10),
          Text(label, style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13, color: color.withOpacity(0.9))),
        ]),
      ),
    );
  }
}

class _StreakCard extends StatelessWidget {
  final int streak;
  final int maxStreak;
  const _StreakCard({required this.streak, required this.maxStreak});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(colors: [AppColors.accent.withOpacity(0.1), AppColors.warning.withOpacity(0.05)]),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.accent.withOpacity(0.2)),
      ),
      child: Row(children: [
        const Text('🔥', style: TextStyle(fontSize: 32)),
        const SizedBox(width: 12),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('$streak day streak!', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          Text('Best: $maxStreak days · Keep going!', style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
        ])),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(color: AppColors.accent, borderRadius: BorderRadius.circular(20)),
          child: const Text('Claim', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 12)),
        ),
      ]),
    );
  }
}
