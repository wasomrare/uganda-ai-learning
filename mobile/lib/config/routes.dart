import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/auth_provider.dart';
import '../screens/auth/login_screen.dart';
import '../screens/auth/splash_screen.dart';
import '../screens/home/home_screen.dart';
import '../screens/subjects/subjects_screen.dart';
import '../screens/subjects/subject_detail_screen.dart';
import '../screens/assessment/assessment_list_screen.dart';
import '../screens/assessment/assessment_screen.dart';
import '../screens/assessment/assessment_result_screen.dart';
import '../screens/ai_tutor/ai_tutor_screen.dart';
import '../screens/gamification/gamification_screen.dart';
import '../screens/leaderboard/leaderboard_screen.dart';
import '../screens/notifications/notifications_screen.dart';
import '../screens/profile/profile_screen.dart';
import '../screens/revision/revision_screen.dart';
import '../screens/teacher/teacher_home_screen.dart';
import '../screens/teacher/teacher_assessments_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final notifier = ValueNotifier<int>(0);
  ref.listen<AsyncValue<AuthState>>(authStateProvider, (_, __) {
    notifier.value++;
  });
  ref.onDispose(notifier.dispose);

  return GoRouter(
    initialLocation: '/splash',
    refreshListenable: notifier,
    redirect: (context, state) {
      final authAsync = ref.read(authStateProvider);
      final isSplash = state.matchedLocation == '/splash';
      final isLogin = state.matchedLocation == '/login';

      // Still loading — stay on splash
      if (authAsync.isLoading) return isSplash ? null : '/splash';

      final isLoggedIn = authAsync.valueOrNull?.isLoggedIn ?? false;
      final role = authAsync.valueOrNull?.user?.role ?? 'student';

      if (isSplash) {
        return isLoggedIn
            ? (role == 'teacher' ? '/teacher' : '/home')
            : '/login';
      }
      if (!isLoggedIn && !isLogin) return '/login';
      if (isLoggedIn && isLogin) {
        return role == 'teacher' ? '/teacher' : '/home';
      }
      return null;
    },
    routes: [
      GoRoute(path: '/splash', builder: (_, __) => const SplashScreen()),
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),

      // Student routes
      ShellRoute(
        builder: (context, state, child) => MainShell(child: child),
        routes: [
          GoRoute(path: '/home', builder: (_, __) => const HomeScreen()),
          GoRoute(path: '/subjects', builder: (_, __) => const SubjectsScreen()),
          GoRoute(
            path: '/subjects/:id',
            builder: (_, state) => SubjectDetailScreen(subjectId: state.pathParameters['id']!),
          ),
          GoRoute(path: '/assessments', builder: (_, __) => const AssessmentListScreen()),
          GoRoute(
            path: '/assessments/:id',
            builder: (_, state) => AssessmentScreen(assessmentId: state.pathParameters['id']!),
          ),
          GoRoute(
            path: '/assessments/:id/result',
            builder: (_, state) => AssessmentResultScreen(attemptId: state.pathParameters['id']!),
          ),
          GoRoute(path: '/ai-tutor', builder: (_, __) => const AiTutorScreen()),
          GoRoute(path: '/gamification', builder: (_, __) => const GamificationScreen()),
          GoRoute(path: '/leaderboard', builder: (_, __) => const LeaderboardScreen()),
          GoRoute(path: '/notifications', builder: (_, __) => const NotificationsScreen()),
          GoRoute(path: '/profile', builder: (_, __) => const ProfileScreen()),
          GoRoute(path: '/revision', builder: (_, __) => const RevisionScreen()),
        ],
      ),

      // Teacher routes
      GoRoute(path: '/teacher', builder: (_, __) => const TeacherHomeScreen()),
      GoRoute(path: '/teacher/assessments', builder: (_, __) => const TeacherAssessmentsScreen()),
    ],
  );
});

class MainShell extends StatefulWidget {
  final Widget child;
  const MainShell({super.key, required this.child});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _currentIndex = 0;

  final _routes = ['/home', '/subjects', '/assessments', '/ai-tutor', '/profile'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: widget.child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (i) {
          setState(() => _currentIndex = i);
          context.go(_routes[i]);
        },
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.book_outlined), selectedIcon: Icon(Icons.book), label: 'Subjects'),
          NavigationDestination(icon: Icon(Icons.quiz_outlined), selectedIcon: Icon(Icons.quiz), label: 'Tests'),
          NavigationDestination(icon: Icon(Icons.smart_toy_outlined), selectedIcon: Icon(Icons.smart_toy), label: 'AI Tutor'),
          NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}
