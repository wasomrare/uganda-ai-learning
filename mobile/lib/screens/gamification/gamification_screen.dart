import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../config/theme.dart';
import '../../services/api_service.dart';

final _gameProfileProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final api = ref.read(apiServiceProvider);
  final res = await api.getGameProfile();
  return res.data['data'] as Map<String, dynamic>? ?? {};
});

final _badgesProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final api = ref.read(apiServiceProvider);
  final res = await api.getBadges();
  final data = res.data['data'];
  if (data is Map && data.containsKey('results')) {
    return List<Map<String, dynamic>>.from(data['results'] as List);
  }
  return List<Map<String, dynamic>>.from(data as List? ?? []);
});

class GamificationScreen extends ConsumerWidget {
  const GamificationScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(_gameProfileProvider);
    final badgesAsync = ref.watch(_badgesProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(title: const Text('Achievements & XP')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // XP Card
            profileAsync.when(
              loading: () => const SizedBox(height: 120, child: Center(child: CircularProgressIndicator())),
              error: (_, __) => const SizedBox.shrink(),
              data: (profile) => _XpCard(profile: profile),
            ),
            const SizedBox(height: 20),

            // Stats row
            profileAsync.when(
              loading: () => const SizedBox.shrink(),
              error: (_, __) => const SizedBox.shrink(),
              data: (profile) => Row(children: [
                Expanded(child: _StatBox(emoji: '🔥', label: 'Streak', value: '${profile['streak_days'] ?? 0} days')),
                const SizedBox(width: 10),
                Expanded(child: _StatBox(emoji: '🏆', label: 'Rank', value: '#${profile['rank'] ?? '--'}')),
                const SizedBox(width: 10),
                Expanded(child: _StatBox(emoji: '⭐', label: 'Level', value: 'Level ${profile['level'] ?? 1}')),
              ]),
            ),
            const SizedBox(height: 24),

            // Badges
            Text('Badges Earned', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            badgesAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (_, __) => const Text('Could not load badges'),
              data: (badges) => badges.isEmpty
                  ? Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(color: AppColors.surface, borderRadius: BorderRadius.circular(14), border: Border.all(color: AppColors.border)),
                    child: const Center(child: Text('No badges yet. Complete assessments to earn them!', textAlign: TextAlign.center, style: TextStyle(color: AppColors.textSecondary))),
                  )
                  : GridView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3, childAspectRatio: 0.85, crossAxisSpacing: 12, mainAxisSpacing: 12),
                    itemCount: badges.length,
                    itemBuilder: (context, i) => _BadgeCard(badge: badges[i]),
                  ),
            ),
          ],
        ),
      ),
    );
  }
}

class _XpCard extends StatelessWidget {
  final Map<String, dynamic> profile;
  const _XpCard({required this.profile});

  @override
  Widget build(BuildContext context) {
    final xp = profile['total_xp'] as int? ?? 0;
    final level = profile['level'] as int? ?? 1;
    final progress = ((xp % 500) / 500).clamp(0.0, 1.0);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [AppColors.primary, AppColors.primaryDark], begin: Alignment.topLeft, end: Alignment.bottomRight),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [BoxShadow(color: AppColors.primary.withOpacity(0.3), blurRadius: 16, offset: const Offset(0, 6))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
            Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              const Text('⭐ Level', style: TextStyle(color: Colors.white70, fontSize: 12)),
              Text('$level', style: const TextStyle(color: Colors.white, fontSize: 36, fontWeight: FontWeight.bold)),
            ]),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(color: Colors.white.withOpacity(0.2), borderRadius: BorderRadius.circular(20)),
              child: Text('$xp XP', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            ),
          ]),
          const SizedBox(height: 16),
          Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
            Text('Progress to Level ${level + 1}', style: TextStyle(color: Colors.white.withOpacity(0.8), fontSize: 12)),
            Text('${xp % 500} / 500 XP', style: TextStyle(color: Colors.white.withOpacity(0.8), fontSize: 12)),
          ]),
          const SizedBox(height: 6),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: progress,
              backgroundColor: Colors.white.withOpacity(0.2),
              valueColor: const AlwaysStoppedAnimation(AppColors.ugandaYellow),
              minHeight: 8,
            ),
          ),
        ],
      ),
    );
  }
}

class _StatBox extends StatelessWidget {
  final String emoji;
  final String label;
  final String value;
  const _StatBox({required this.emoji, required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(children: [
        Text(emoji, style: const TextStyle(fontSize: 24)),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
        Text(label, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
      ]),
    );
  }
}

class _BadgeCard extends StatelessWidget {
  final Map<String, dynamic> badge;
  const _BadgeCard({required this.badge});

  @override
  Widget build(BuildContext context) {
    final earned = badge['is_earned'] as bool? ?? false;
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: earned ? AppColors.xpGold.withOpacity(0.05) : AppColors.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: earned ? AppColors.xpGold.withOpacity(0.4) : AppColors.border),
      ),
      child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
        Container(
          width: 48, height: 48,
          decoration: BoxDecoration(
            color: earned ? AppColors.xpGold.withOpacity(0.15) : AppColors.border.withOpacity(0.5),
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              badge['icon'] as String? ?? '🏅',
              style: TextStyle(fontSize: 24, color: earned ? null : Colors.grey),
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(badge['name'] as String? ?? '', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: earned ? AppColors.textPrimary : AppColors.textHint), textAlign: TextAlign.center, maxLines: 2, overflow: TextOverflow.ellipsis),
        if (!earned) const Text('Locked', style: TextStyle(fontSize: 10, color: AppColors.textHint)),
      ]),
    );
  }
}
