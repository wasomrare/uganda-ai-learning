import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'storage_service.dart';
import '../config/constants.dart';

final apiServiceProvider = Provider<ApiService>((ref) {
  final storage = ref.read(storageServiceProvider);
  return ApiService(storage);
});

class ApiService {
  late final Dio _dio;
  final StorageService _storage;

  ApiService(this._storage) {
    _dio = Dio(BaseOptions(
      baseUrl: AppConstants.baseUrl,
      connectTimeout: const Duration(seconds: AppConstants.connectTimeout),
      receiveTimeout: const Duration(seconds: AppConstants.receiveTimeout),
      sendTimeout: const Duration(seconds: AppConstants.connectTimeout),
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.getAccessToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (error, handler) async {
        final isNetworkError = error.type == DioExceptionType.connectionTimeout ||
            error.type == DioExceptionType.receiveTimeout ||
            error.type == DioExceptionType.connectionError;
        final retryCount = error.requestOptions.extra['retryCount'] ?? 0;
        if (isNetworkError && retryCount < 2) {
          error.requestOptions.extra['retryCount'] = retryCount + 1;
          await Future.delayed(Duration(seconds: retryCount + 1));
          try {
            final response = await _dio.fetch(error.requestOptions);
            return handler.resolve(response);
          } catch (_) {}
        }
        if (error.response?.statusCode == 401) {
          final refreshed = await _refreshToken();
          if (refreshed) {
            final token = await _storage.getAccessToken();
            error.requestOptions.headers['Authorization'] = 'Bearer $token';
            final response = await _dio.fetch(error.requestOptions);
            return handler.resolve(response);
          }
        }
        return handler.next(error);
      },
    ));
  }

  Future<bool> _refreshToken() async {
    try {
      final refresh = await _storage.getRefreshToken();
      if (refresh == null) return false;
      final res = await _dio.post('/auth/refresh/', data: {'refresh': refresh});
      await _storage.saveAccessToken(res.data['access']);
      return true;
    } catch (_) {
      await _storage.clearTokens();
      return false;
    }
  }

  Future<Response> get(String path, {Map<String, dynamic>? params}) =>
      _dio.get(path, queryParameters: params);

  Future<Response> post(String path, {dynamic data}) =>
      _dio.post(path, data: data);

  Future<Response> patch(String path, {dynamic data}) =>
      _dio.patch(path, data: data);

  Future<Response> delete(String path) =>
      _dio.delete(path);

  // Auth
  Future<Response> register({
    required String firstName,
    required String lastName,
    required String username,
    required String password,
    required String confirmPassword,
    String role = 'student',
    String? email,
  }) => _dio.post('/auth/register/', data: {
    'first_name': firstName,
    'last_name': lastName,
    'username': username,
    'password': password,
    'confirm_password': confirmPassword,
    'role': role,
    if (email != null && email.isNotEmpty) 'email': email,
  });

  Future<Response> login(String username, String password) =>
      _dio.post('/auth/login/', data: {'username': username, 'password': password});

  Future<Response> googleLogin(String idToken) =>
      _dio.post('/auth/google/', data: {'id_token': idToken});

  Future<Response> logout(String refresh) =>
      _dio.post('/auth/logout/', data: {'refresh': refresh});

  Future<Response> getMe() => _dio.get('/auth/me/');

  // Dashboard
  Future<Response> getStudentDashboard() => _dio.get('/dashboard/student/');
  Future<Response> getTeacherDashboard() => _dio.get('/dashboard/teacher/');

  // Subjects
  Future<Response> getSubjects() => _dio.get('/subjects/');
  Future<Response> getCurriculum({required String classLevel, required String subjectId}) =>
      _dio.get('/curriculum/', queryParameters: {'class_level': classLevel, 'subject': subjectId});

  // Assessments
  Future<Response> getMyAssessments({Map<String, dynamic>? params}) =>
      _dio.get('/assessments/', queryParameters: params);
  Future<Response> getAssessment(String id) => _dio.get('/assessments/$id/');
  Future<Response> startAttempt(String assessmentId) =>
      _dio.post('/assessments/$assessmentId/start/');
  Future<Response> submitAttempt(String attemptId, List<Map<String, dynamic>> answers) =>
      _dio.post('/assessments/attempts/$attemptId/submit/', data: {'answers': answers});
  Future<Response> getAttemptResult(String attemptId) =>
      _dio.get('/assessments/attempts/$attemptId/');

  // AI
  Future<Response> aiChat(String message, {String? subjectId, String? topicId}) =>
      _dio.post('/ai/chat/', data: {'message': message, 'subject_id': subjectId, 'topic_id': topicId});

  // Gamification
  Future<Response> getGameProfile() => _dio.get('/gamification/profile/');
  Future<Response> getBadges() => _dio.get('/gamification/badges/');

  // Leaderboard
  Future<Response> getWeeklyLeaderboard({String? classLevel}) =>
      _dio.get('/leaderboards/weekly/', queryParameters: {'class_level': classLevel});

  // Notifications
  Future<Response> getNotifications() => _dio.get('/notifications/mine/');
  Future<Response> markNotificationRead(String id) =>
      _dio.post('/notifications/$id/mark-read/');

  // Revision
  Future<Response> startRevisionSession(Map<String, dynamic> data) =>
      _dio.post('/revision/start/', data: data);

  // Reports
  Future<Response> getMyReports() => _dio.get('/reports/');

  // Student analytics
  Future<Response> getStudentAnalytics() => _dio.get('/analytics/student/me/');
}
