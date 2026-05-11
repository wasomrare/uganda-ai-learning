import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/auth_provider.dart';
import '../../config/theme.dart';

class SplashScreen extends ConsumerWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.listen(authStateProvider, (_, next) {
      next.whenData((state) {
        if (state.isLoggedIn) {
          final role = state.user?.role ?? 'student';
          Future.delayed(const Duration(milliseconds: 500), () {
            if (context.mounted) {
              context.go(role == 'teacher' || role == 'super_admin' ? '/teacher' : '/home');
            }
          });
        } else {
          Future.delayed(const Duration(milliseconds: 500), () {
            if (context.mounted) context.go('/login');
          });
        }
      });
    });

    return Scaffold(
      backgroundColor: AppColors.primary,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 80, height: 80,
              decoration: BoxDecoration(color: Colors.white.withOpacity(0.2), borderRadius: BorderRadius.circular(24)),
              child: const Icon(Icons.school_rounded, size: 48, color: Colors.white),
            ),
            const SizedBox(height: 20),
            const Text('Uganda AI Learning',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white)),
            const SizedBox(height: 8),
            Text('Powered by AI · UNEB Curriculum',
              style: TextStyle(fontSize: 13, color: Colors.white.withOpacity(0.8))),
            const SizedBox(height: 48),
            const CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
          ],
        ),
      ),
    );
  }
}
