import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../config/theme.dart';
import '../../services/api_service.dart';
import '../../models/assessment_model.dart';
import 'dart:async';

class AssessmentScreen extends ConsumerStatefulWidget {
  final String assessmentId;
  const AssessmentScreen({super.key, required this.assessmentId});

  @override
  ConsumerState<AssessmentScreen> createState() => _AssessmentScreenState();
}

class _AssessmentScreenState extends ConsumerState<AssessmentScreen> {
  List<QuestionModel> _questions = [];
  Map<String, String> _answers = {};
  String? _attemptId;
  int _currentIndex = 0;
  late Timer _timer;
  int _secondsRemaining = 0;
  bool _loading = true;
  bool _submitting = false;

  @override
  void initState() {
    super.initState();
    _startAssessment();
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  Future<void> _startAssessment() async {
    try {
      final api = ref.read(apiServiceProvider);
      final res = await api.startAttempt(widget.assessmentId);
      final data = res.data['data'] as Map<String, dynamic>;
      _attemptId = data['attempt_id'] as String;
      final qs = (data['questions'] as List<dynamic>? ?? [])
          .map((q) => QuestionModel.fromJson(q as Map<String, dynamic>))
          .toList();
      final duration = (data['duration_minutes'] as int? ?? 60) * 60;

      setState(() {
        _questions = qs;
        _secondsRemaining = duration;
        _loading = false;
      });

      _timer = Timer.periodic(const Duration(seconds: 1), (t) {
        if (_secondsRemaining <= 0) {
          t.cancel();
          _submit();
        } else {
          setState(() => _secondsRemaining--);
        }
      });
    } catch (e) {
      setState(() => _loading = false);
      if (mounted) context.pop();
    }
  }

  Future<void> _submit() async {
    if (_submitting || _attemptId == null) return;
    setState(() => _submitting = true);
    _timer.cancel();
    try {
      final api = ref.read(apiServiceProvider);
      final answers = _answers.entries
          .map((e) => {'question_id': e.key, 'answer': e.value})
          .toList();
      await api.submitAttempt(_attemptId!, answers);
      if (mounted) context.go('/assessments/$_attemptId/result');
    } catch (e) {
      setState(() => _submitting = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Submit failed: $e'), backgroundColor: AppColors.error),
        );
      }
    }
  }

  String get _timerText {
    final m = _secondsRemaining ~/ 60;
    final s = _secondsRemaining % 60;
    return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
  }

  Color get _timerColor => _secondsRemaining < 300 ? AppColors.error : AppColors.primary;

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Scaffold(
        backgroundColor: AppColors.background,
        body: Center(
          child: Column(mainAxisAlignment: MainAxisAlignment.center, children: const [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Starting assessment…'),
          ]),
        ),
      );
    }

    if (_questions.isEmpty) {
      return Scaffold(
        appBar: AppBar(title: const Text('Assessment')),
        body: const Center(child: Text('No questions available.')),
      );
    }

    final q = _questions[_currentIndex];
    final progress = (_currentIndex + 1) / _questions.length;

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, _) async {
        if (didPop) return;
        final confirm = await showDialog<bool>(
          context: context,
          builder: (_) => AlertDialog(
            title: const Text('Leave Assessment?'),
            content: const Text('Your progress will be submitted automatically.'),
            actions: [
              TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Stay')),
              ElevatedButton(onPressed: () => Navigator.pop(context, true), child: const Text('Leave')),
            ],
          ),
        );
        if (confirm == true) await _submit();
      },
      child: Scaffold(
        backgroundColor: AppColors.background,
        appBar: AppBar(
          automaticallyImplyLeading: false,
          title: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Q ${_currentIndex + 1}/${_questions.length}', style: const TextStyle(fontSize: 13, color: AppColors.textSecondary)),
              LinearProgressIndicator(
                value: progress,
                backgroundColor: AppColors.border,
                valueColor: const AlwaysStoppedAnimation(AppColors.primary),
                minHeight: 4,
                borderRadius: BorderRadius.circular(2),
              ),
            ],
          ),
          actions: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(color: _timerColor.withOpacity(0.1), borderRadius: BorderRadius.circular(20)),
              child: Row(children: [
                Icon(Icons.timer_outlined, size: 14, color: _timerColor),
                const SizedBox(width: 4),
                Text(_timerText, style: TextStyle(fontWeight: FontWeight.bold, color: _timerColor, fontSize: 14)),
              ]),
            ),
            const SizedBox(width: 12),
          ],
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Question
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(color: AppColors.surface, borderRadius: BorderRadius.circular(16), border: Border.all(color: AppColors.border)),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(color: AppColors.primaryLight, borderRadius: BorderRadius.circular(6)),
                        child: Text('${q.marks} mark${q.marks != 1 ? 's' : ''}', style: const TextStyle(fontSize: 11, color: AppColors.primary, fontWeight: FontWeight.w600)),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(color: AppColors.border, borderRadius: BorderRadius.circular(6)),
                        child: Text(q.difficulty, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                      ),
                    ]),
                    const SizedBox(height: 12),
                    Text(q.questionText, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500, height: 1.5)),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Options (MCQ)
              if (q.questionType == 'mcq') ...[
                ...q.options.map((opt) {
                  final isSelected = _answers[q.id] == opt.id;
                  return GestureDetector(
                    onTap: () => setState(() => _answers[q.id] = opt.id),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 200),
                      margin: const EdgeInsets.only(bottom: 10),
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: isSelected ? AppColors.primaryLight : AppColors.surface,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: isSelected ? AppColors.primary : AppColors.border, width: isSelected ? 2 : 1),
                      ),
                      child: Row(children: [
                        Container(
                          width: 32, height: 32,
                          decoration: BoxDecoration(
                            color: isSelected ? AppColors.primary : AppColors.border,
                            shape: BoxShape.circle,
                          ),
                          child: Center(child: Text(opt.label, style: TextStyle(fontWeight: FontWeight.bold, color: isSelected ? Colors.white : AppColors.textSecondary, fontSize: 13))),
                        ),
                        const SizedBox(width: 12),
                        Expanded(child: Text(opt.text, style: TextStyle(fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal))),
                        if (isSelected) const Icon(Icons.check_circle, color: AppColors.primary, size: 20),
                      ]),
                    ),
                  );
                }),
              ] else ...[
                // Text input for other types
                TextFormField(
                  initialValue: _answers[q.id],
                  maxLines: q.questionType == 'composition' ? 8 : 3,
                  decoration: InputDecoration(
                    hintText: q.questionType == 'composition' ? 'Write your essay here…' : 'Your answer…',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  onChanged: (v) => _answers[q.id] = v,
                ),
              ],

              const SizedBox(height: 32),
            ],
          ),
        ),
        bottomNavigationBar: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                if (_currentIndex > 0)
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => setState(() => _currentIndex--),
                      child: const Text('Previous'),
                    ),
                  ),
                if (_currentIndex > 0) const SizedBox(width: 12),
                Expanded(
                  flex: 2,
                  child: ElevatedButton(
                    onPressed: _submitting ? null : () {
                      if (_currentIndex < _questions.length - 1) {
                        setState(() => _currentIndex++);
                      } else {
                        _submit();
                      }
                    },
                    style: ElevatedButton.styleFrom(backgroundColor: _currentIndex == _questions.length - 1 ? AppColors.success : AppColors.primary),
                    child: _submitting
                        ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                        : Text(_currentIndex == _questions.length - 1 ? 'Submit' : 'Next', style: const TextStyle(color: Colors.white)),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
