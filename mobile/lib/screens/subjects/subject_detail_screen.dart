import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../config/theme.dart';
import '../../services/api_service.dart';

final _subjectDetailProvider = FutureProvider.family<Map<String, dynamic>, String>((ref, subjectId) async {
  final api = ref.read(apiServiceProvider);
  final res = await api.get('/subjects/$subjectId/');
  return res.data['data'] as Map<String, dynamic>? ?? {};
});

final _topicsProvider = FutureProvider.family<List<Map<String, dynamic>>, String>((ref, subjectId) async {
  final api = ref.read(apiServiceProvider);
  final res = await api.get('/curriculum/', params: {'subject': subjectId});
  final data = res.data['data'];
  if (data is Map && data.containsKey('results')) {
    return List<Map<String, dynamic>>.from(data['results'] as List);
  }
  return List<Map<String, dynamic>>.from(data as List? ?? []);
});

class SubjectDetailScreen extends ConsumerWidget {
  final String subjectId;
  const SubjectDetailScreen({super.key, required this.subjectId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final subjectAsync = ref.watch(_subjectDetailProvider(subjectId));
    final topicsAsync = ref.watch(_topicsProvider(subjectId));

    return Scaffold(
      backgroundColor: AppColors.background,
      body: subjectAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (subject) => CustomScrollView(
          slivers: [
            SliverAppBar(
              expandedHeight: 160,
              pinned: true,
              backgroundColor: AppColors.primary,
              foregroundColor: Colors.white,
              flexibleSpace: FlexibleSpaceBar(
                title: Text(subject['name'] as String? ?? 'Subject', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                background: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(colors: [AppColors.primary, AppColors.primaryDark], begin: Alignment.topLeft, end: Alignment.bottomRight),
                  ),
                  child: Center(child: Text('📚', style: const TextStyle(fontSize: 64))),
                ),
              ),
              actions: [
                IconButton(
                  icon: const Icon(Icons.smart_toy_outlined, color: Colors.white),
                  onPressed: () => context.push('/ai-tutor'),
                ),
              ],
            ),
            SliverPadding(
              padding: const EdgeInsets.all(16),
              sliver: topicsAsync.when(
                loading: () => const SliverToBoxAdapter(child: Center(child: CircularProgressIndicator())),
                error: (e, _) => SliverToBoxAdapter(child: Text('Error loading topics: $e')),
                data: (topics) => SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, i) {
                      if (i == 0) {
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: Text('Topics (${topics.length})', style: Theme.of(context).textTheme.titleMedium),
                        );
                      }
                      final topic = topics[i - 1];
                      return Container(
                        margin: const EdgeInsets.only(bottom: 10),
                        decoration: BoxDecoration(
                          color: AppColors.surface,
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(color: AppColors.border),
                        ),
                        child: ListTile(
                          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          leading: CircleAvatar(
                            backgroundColor: AppColors.primaryLight,
                            child: Text('${i}', style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold)),
                          ),
                          title: Text(topic['name'] as String? ?? '', style: const TextStyle(fontWeight: FontWeight.w600)),
                          subtitle: topic['description'] != null ? Text(topic['description'] as String, maxLines: 2, overflow: TextOverflow.ellipsis) : null,
                          trailing: const Icon(Icons.arrow_forward_ios, size: 14, color: AppColors.textHint),
                          onTap: () => context.push('/ai-tutor?subject=$subjectId&topic=${topic['id']}'),
                        ),
                      );
                    },
                    childCount: topics.length + 1,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
