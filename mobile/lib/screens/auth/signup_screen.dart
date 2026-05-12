import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../config/theme.dart';
import '../../providers/auth_provider.dart';

class SignupScreen extends ConsumerStatefulWidget {
  const SignupScreen({super.key});

  @override
  ConsumerState<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends ConsumerState<SignupScreen> {
  final _formKey = GlobalKey<FormState>();
  final _firstNameCtrl = TextEditingController();
  final _lastNameCtrl = TextEditingController();
  final _usernameCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  final _confirmCtrl = TextEditingController();
  String _role = 'student';
  bool _obscurePw = true;
  bool _obscureConfirm = true;
  bool _loading = false;

  @override
  void dispose() {
    _firstNameCtrl.dispose();
    _lastNameCtrl.dispose();
    _usernameCtrl.dispose();
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    _confirmCtrl.dispose();
    super.dispose();
  }

  Future<void> _register() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    await ref.read(authStateProvider.notifier).register(
      firstName: _firstNameCtrl.text.trim(),
      lastName: _lastNameCtrl.text.trim(),
      username: _usernameCtrl.text.trim(),
      password: _passwordCtrl.text,
      confirmPassword: _confirmCtrl.text,
      role: _role,
      email: _emailCtrl.text.trim().isEmpty ? null : _emailCtrl.text.trim(),
    );
    setState(() => _loading = false);
    final authState = ref.read(authStateProvider).valueOrNull;
    if (!mounted) return;
    if (authState?.error != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(authState!.error!), backgroundColor: AppColors.error),
      );
    } else if (authState?.isLoggedIn == true) {
      final role = authState!.user?.role ?? 'student';
      context.go(role == 'teacher' ? '/teacher' : '/home');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
          onPressed: () => context.go('/login'),
        ),
        title: const Text('Create Account', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 4),
                Text('Who are you?', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
                const SizedBox(height: 10),
                _RoleSelector(selected: _role, onChanged: (r) => setState(() => _role = r)),
                const SizedBox(height: 20),
                Text('Your details', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
                const SizedBox(height: 12),

                // Name row
                Row(children: [
                  Expanded(child: _Field(ctrl: _firstNameCtrl, label: 'First Name', hint: 'e.g. John',
                    validator: (v) => (v == null || v.isEmpty) ? 'Required' : null)),
                  const SizedBox(width: 12),
                  Expanded(child: _Field(ctrl: _lastNameCtrl, label: 'Last Name', hint: 'e.g. Doe',
                    validator: (v) => (v == null || v.isEmpty) ? 'Required' : null)),
                ]),
                const SizedBox(height: 14),

                // Username
                _Field(
                  ctrl: _usernameCtrl,
                  label: 'Username',
                  hint: 'Choose a unique username',
                  prefixIcon: Icons.person_outline,
                  validator: (v) {
                    if (v == null || v.isEmpty) return 'Username is required';
                    if (v.length < 3) return 'At least 3 characters';
                    if (v.contains(' ')) return 'No spaces allowed';
                    return null;
                  },
                ),
                const SizedBox(height: 14),

                // Email (optional)
                _Field(
                  ctrl: _emailCtrl,
                  label: 'Email (optional)',
                  hint: 'your@email.com',
                  prefixIcon: Icons.email_outlined,
                  keyboardType: TextInputType.emailAddress,
                  validator: (v) {
                    if (v == null || v.isEmpty) return null;
                    final emailRegex = RegExp(r'^[^@]+@[^@]+\.[^@]+$');
                    if (!emailRegex.hasMatch(v)) return 'Invalid email address';
                    return null;
                  },
                ),
                const SizedBox(height: 14),

                // Password
                _PasswordField(
                  ctrl: _passwordCtrl,
                  label: 'Password',
                  hint: 'Min 6 characters',
                  obscure: _obscurePw,
                  onToggle: () => setState(() => _obscurePw = !_obscurePw),
                  validator: (v) {
                    if (v == null || v.isEmpty) return 'Password is required';
                    if (v.length < 6) return 'At least 6 characters';
                    return null;
                  },
                ),
                const SizedBox(height: 14),

                // Confirm password
                _PasswordField(
                  ctrl: _confirmCtrl,
                  label: 'Confirm Password',
                  hint: 'Repeat your password',
                  obscure: _obscureConfirm,
                  onToggle: () => setState(() => _obscureConfirm = !_obscureConfirm),
                  validator: (v) {
                    if (v == null || v.isEmpty) return 'Please confirm your password';
                    if (v != _passwordCtrl.text) return 'Passwords do not match';
                    return null;
                  },
                ),
                const SizedBox(height: 28),

                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _loading ? null : _register,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                    ),
                    child: _loading
                        ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                        : const Text('Create Account', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600)),
                  ),
                ),
                const SizedBox(height: 16),
                Center(
                  child: GestureDetector(
                    onTap: () => context.go('/login'),
                    child: RichText(
                      text: TextSpan(
                        text: 'Already have an account? ',
                        style: const TextStyle(color: AppColors.textSecondary, fontSize: 13),
                        children: [
                          TextSpan(
                            text: 'Sign In',
                            style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _RoleSelector extends StatelessWidget {
  final String selected;
  final ValueChanged<String> onChanged;
  const _RoleSelector({required this.selected, required this.onChanged});

  static const _roles = [
    {'value': 'student', 'label': 'Student', 'icon': '🎓', 'desc': 'P.1 – P.7 Learner'},
    {'value': 'teacher', 'label': 'Teacher', 'icon': '📖', 'desc': 'Classroom Teacher'},
    {'value': 'parent', 'label': 'Parent', 'icon': '👨‍👩‍👧', 'desc': 'Parent / Guardian'},
  ];

  @override
  Widget build(BuildContext context) {
    return Row(
      children: _roles.map((r) {
        final active = selected == r['value'];
        return Expanded(
          child: GestureDetector(
            onTap: () => onChanged(r['value']!),
            child: Container(
              margin: const EdgeInsets.only(right: 8),
              padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 4),
              decoration: BoxDecoration(
                color: active ? AppColors.primary.withOpacity(0.08) : Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: active ? AppColors.primary : const Color(0xFFE5E7EB),
                  width: active ? 2 : 1,
                ),
              ),
              child: Column(mainAxisSize: MainAxisSize.min, children: [
                Text(r['icon']!, style: const TextStyle(fontSize: 22)),
                const SizedBox(height: 4),
                Text(r['label']!, style: TextStyle(
                  fontSize: 12, fontWeight: FontWeight.bold,
                  color: active ? AppColors.primary : AppColors.textPrimary,
                )),
                Text(r['desc']!, style: const TextStyle(fontSize: 9, color: AppColors.textSecondary), textAlign: TextAlign.center),
              ]),
            ),
          ),
        );
      }).toList(),
    );
  }
}

class _Field extends StatelessWidget {
  final TextEditingController ctrl;
  final String label;
  final String hint;
  final IconData? prefixIcon;
  final TextInputType? keyboardType;
  final String? Function(String?)? validator;

  const _Field({
    required this.ctrl, required this.label, required this.hint,
    this.prefixIcon, this.keyboardType, this.validator,
  });

  @override
  Widget build(BuildContext context) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500, color: AppColors.textPrimary)),
      const SizedBox(height: 6),
      TextFormField(
        controller: ctrl,
        keyboardType: keyboardType,
        validator: validator,
        decoration: InputDecoration(
          hintText: hint,
          prefixIcon: prefixIcon != null ? Icon(prefixIcon, size: 18) : null,
        ),
      ),
    ]);
  }
}

class _PasswordField extends StatelessWidget {
  final TextEditingController ctrl;
  final String label;
  final String hint;
  final bool obscure;
  final VoidCallback onToggle;
  final String? Function(String?)? validator;

  const _PasswordField({
    required this.ctrl, required this.label, required this.hint,
    required this.obscure, required this.onToggle, this.validator,
  });

  @override
  Widget build(BuildContext context) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500, color: AppColors.textPrimary)),
      const SizedBox(height: 6),
      TextFormField(
        controller: ctrl,
        obscureText: obscure,
        validator: validator,
        decoration: InputDecoration(
          hintText: hint,
          prefixIcon: const Icon(Icons.lock_outline, size: 18),
          suffixIcon: IconButton(
            icon: Icon(obscure ? Icons.visibility_off_outlined : Icons.visibility_outlined, size: 18),
            onPressed: onToggle,
          ),
        ),
      ),
    ]);
  }
}
