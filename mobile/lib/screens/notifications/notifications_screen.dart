import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../config/theme.dart';
import '../../services/api_service.dart';

final _notificationsProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final api = ref.read(apiServiceProvider);
  final res = await api.getNotifications();
  final data = res.data['data'];
  if (data is Map && data.containsKey('results')) {
    return List<Map<String, dynamic>>.from(data['results'] as List);
  }
  return List<Map<String, dynamic>>.from(data as List? ?? []);
});

class NotificationsScreen extends ConsumerWidget {
  const NotificationsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final notifAsync = ref.watch(_notificationsProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(title: const Text('Notifications')),
      body: notifAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (notifs) => notifs.isEmpty
            ? Center(
                child: Column(mainAxisAlignment: MainAxisAlignment.center, children: const [
                  Icon(Icons.notifications_none, size: 64, color: AppColors.textHint),
                  SizedBox(height: 12),
                  Text('No notifications yet', style: TextStyle(color: AppColors.textSecondary, fontSize: 16)),
                ]),
              )
            : ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: notifs.length,
                separatorBuilder: (_, __) => const SizedBox(height: 8),
                itemBuilder: (context, i) {
                  final n = notifs[i];
                  final isRead = n['is_read'] as bool? ?? false;
                  return Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: isRead ? AppColors.surface : AppColors.primaryLight.withOpacity(0.5),
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: isRead ? AppColors.border : AppColors.primary.withOpacity(0.2)),
                    ),
                    child: Row(children: [
                      Container(
                        width: 40, height: 40,
                        decoration: BoxDecoration(color: AppColors.primary.withOpacity(0.1), shape: BoxShape.circle),
                        child: const Icon(Icons.notifications_outlined, color: AppColors.primary, size: 20),
                      ),
                      const SizedBox(width: 12),
                      Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                        Text(n['title'] as String? ?? '', style: TextStyle(fontWeight: isRead ? FontWeight.normal : FontWeight.w600)),
                        if (n['message'] != null) ...[
                          const SizedBox(height: 2),
                          Text(n['message'] as String, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary), maxLines: 2, overflow: TextOverflow.ellipsis),
                        ],
                      ])),
                      if (!isRead) Container(width: 8, height: 8, decoration: const BoxDecoration(color: AppColors.primary, shape: BoxShape.circle)),
                    ]),
                  );
                },
              ),
      ),
    );
  }
}
