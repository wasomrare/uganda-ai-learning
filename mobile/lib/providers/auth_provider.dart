import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_sign_in/google_sign_in.dart';
import '../config/constants.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';

final _googleSignIn = GoogleSignIn(
  scopes: ['email', 'profile'],
  serverClientId: AppConstants.googleWebClientId,
);

class AuthState {
  final UserModel? user;
  final bool isLoggedIn;
  final bool isLoading;
  final String? error;

  const AuthState({
    this.user,
    this.isLoggedIn = false,
    this.isLoading = false,
    this.error,
  });

  AuthState copyWith({UserModel? user, bool? isLoggedIn, bool? isLoading, String? error}) =>
      AuthState(
        user: user ?? this.user,
        isLoggedIn: isLoggedIn ?? this.isLoggedIn,
        isLoading: isLoading ?? this.isLoading,
        error: error,
      );
}

final authStateProvider = AsyncNotifierProvider<AuthNotifier, AuthState>(AuthNotifier.new);

class AuthNotifier extends AsyncNotifier<AuthState> {
  @override
  Future<AuthState> build() async {
    final storage = ref.read(storageServiceProvider);
    final hasToken = await storage.hasTokens();
    if (!hasToken) return const AuthState(isLoggedIn: false);

    try {
      final userData = await storage.getUser();
      if (userData != null) {
        final user = UserModel.fromJson(userData);
        return AuthState(user: user, isLoggedIn: true);
      }
      return const AuthState(isLoggedIn: false);
    } catch (_) {
      return const AuthState(isLoggedIn: false);
    }
  }

  Future<void> login(String username, String password) async {
    state = const AsyncValue.loading();
    try {
      final api = ref.read(apiServiceProvider);
      final storage = ref.read(storageServiceProvider);
      final res = await api.login(username, password);
      final data = res.data['data'];
      await storage.saveAccessToken(data['access']);
      await storage.saveRefreshToken(data['refresh']);
      final user = UserModel.fromJson(data['user'] as Map<String, dynamic>);
      await storage.saveUser(user.toJson());
      state = AsyncValue.data(AuthState(user: user, isLoggedIn: true));
    } catch (e) {
      state = AsyncValue.data(AuthState(
        isLoggedIn: false,
        error: _parseError(e),
      ));
    }
  }

  Future<void> googleLogin() async {
    state = const AsyncValue.loading();
    try {
      final account = await _googleSignIn.signIn();
      if (account == null) {
        state = const AsyncValue.data(AuthState(isLoggedIn: false));
        return;
      }
      final auth = await account.authentication;
      final idToken = auth.idToken;
      if (idToken == null) {
        state = AsyncValue.data(const AuthState(
          isLoggedIn: false,
          error: 'Could not get Google ID token. Please try again.',
        ));
        return;
      }
      final api = ref.read(apiServiceProvider);
      final storage = ref.read(storageServiceProvider);
      final res = await api.googleLogin(idToken);
      final data = res.data['data'];
      await storage.saveAccessToken(data['access']);
      await storage.saveRefreshToken(data['refresh']);
      final user = UserModel.fromJson(data['user'] as Map<String, dynamic>);
      await storage.saveUser(user.toJson());
      state = AsyncValue.data(AuthState(user: user, isLoggedIn: true));
    } catch (e) {
      await _googleSignIn.signOut();
      state = AsyncValue.data(AuthState(
        isLoggedIn: false,
        error: _parseError(e),
      ));
    }
  }

  Future<void> logout() async {
    try {
      final storage = ref.read(storageServiceProvider);
      final api = ref.read(apiServiceProvider);
      final refresh = await storage.getRefreshToken();
      if (refresh != null) await api.logout(refresh);
      await storage.clearTokens();
    } catch (_) {
      final storage = ref.read(storageServiceProvider);
      await storage.clearTokens();
    }
    state = const AsyncValue.data(AuthState(isLoggedIn: false));
  }

  String _parseError(dynamic e) {
    if (e.toString().contains('401')) return 'Invalid username or password.';
    if (e.toString().contains('network')) return 'Network error. Check your connection.';
    return 'Login failed. Please try again.';
  }
}
