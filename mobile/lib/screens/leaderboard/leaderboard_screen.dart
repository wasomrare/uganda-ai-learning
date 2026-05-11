import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../config/theme.dart';
import '../../services/api_service.dart';

final _leaderboardProvider = FutureProvider.family<List<Map<String, dynamic>>, String?>((ref, classLevel) async {
  final api = ref.read(apiServiceProvider);
  final res = await api.getWeeklyLeaderboard(classLevel: classLevel);
  final data = res.data['data'];
  if (data is Map && data.containsKey('results')) {
    return List<Map<String, dynamic>>.from(data['results'] as List);
  }
  return List<Map<String, dynamic>>.from(data as List? ?? []);
});

class LeaderboardScreen extends ConsumerStatefulWidget {
  const LeaderboardScreen({super.key});

  @override
  ConsumerState<LeaderboardScreen> createState() => _LeaderboardScreenState();
}

class _LeaderboardScreenState extends ConsumerState<LeaderboardScreen> {
  String? _selectedClass;

  @override
  Widget build(BuildContext context) {
    final leaderboardAsync = ref.watch(_leaderboardProvider(_selectedClass));

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Leaderboard'),
        actions: [
          DropdownButton<String?>(
            value: _selectedClass,
            hint: const Text('All', style: TextStyle(color: AppColors.textSecondary)),
            underline: const SizedBox.shrink(),
            items: [
              const DropdownMenuItem(value: null, child: Text('All Classes')),
              ...['P1','P2','P3','P4','P5','P6','P7'].map((l) => DropdownMenuItem(value: l, child: Text(l))),
            ],
            onChanged: (v) => setState(() => _selectedClass = v),
          ),
          const SizedBox(width: 12),
        ],
      ),
      body: leaderboardAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (entries) {
          if (entries.isEmpty) {
            return const Center(child: Text('No data yet.', style: TextStyle(color: AppColors.textSecondary)));
          }
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: entries.length,
            itemBuilder: (context, i) {
              final e = entries[i];
              final rank = i + 1;
              final medals = {1: '🥇', 2: '🥈', 3: '🥉'};
              return Container(
                margin: const EdgeInsets.only(bottom: 10),
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: rank <= 3 ? AppColors.xpGold.withOpacity(0.05) : AppColors.surface,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: rank <= 3 ? AppColors.xpGold.withOpacity(0.3) : AppColors.border),
                ),
                child: Row(children: [
                  SizedBox(
                    width: 36,
                    child: medals.containsKey(rank)
                        ? Text(medals[rank]!, style: const TextStyle(fontSize: 24))
                        : Text('$rank', style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.textSecondary)),
                  ),
                  const SizedBox(width: 10),
                  CircleAvatar(
                    radius: 18, backgroundColor: AppColors.primaryLight,
                    child: Text(
                      (e['user_name'] as String? ?? '?').substring(0, 1).toUpperCase(),
                      style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Text(e['user_name'] as String? ?? '', style: const TextStyle(fontWeight: FontWeight.w600)),
                    Text('${e['class_level'] ?? ''} · ${e['total_xp'] ?? 0} XP', style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                  ])),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(color: AppColors.primaryLight, borderRadius: BorderRadius.circular(12)),
                    child: Text('${e['score'] ?? 0}', style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.primary, fontSize: 13)),
                  ),
                ]),
              );
            },
          );
        },
      ),
    );
  }
}
