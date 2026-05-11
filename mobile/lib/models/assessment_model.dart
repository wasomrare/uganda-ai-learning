class AssessmentModel {
  final String id;
  final String title;
  final String assessmentType;
  final String classLevel;
  final String subjectName;
  final String? subjectId;
  final int totalMarks;
  final int durationMinutes;
  final String status;
  final int questionCount;
  final int term;
  final DateTime? createdAt;

  const AssessmentModel({
    required this.id,
    required this.title,
    required this.assessmentType,
    required this.classLevel,
    required this.subjectName,
    this.subjectId,
    required this.totalMarks,
    required this.durationMinutes,
    required this.status,
    required this.questionCount,
    required this.term,
    this.createdAt,
  });

  factory AssessmentModel.fromJson(Map<String, dynamic> json) => AssessmentModel(
    id: json['id'] as String,
    title: json['title'] as String,
    assessmentType: json['assessment_type'] as String? ?? 'custom',
    classLevel: json['class_level'] as String? ?? '',
    subjectName: (json['subject'] as Map<String, dynamic>?)?['name'] as String? ?? '',
    subjectId: (json['subject'] as Map<String, dynamic>?)?['id'] as String?,
    totalMarks: json['total_marks'] as int? ?? 0,
    durationMinutes: json['duration_minutes'] as int? ?? 60,
    status: json['status'] as String? ?? 'draft',
    questionCount: json['question_count'] as int? ?? 0,
    term: json['term'] as int? ?? 1,
    createdAt: json['created_at'] != null ? DateTime.tryParse(json['created_at']) : null,
  );
}

class QuestionModel {
  final String id;
  final String questionType;
  final String questionText;
  final int marks;
  final String difficulty;
  final List<MCQOptionModel> options;
  final String? imageUrl;

  const QuestionModel({
    required this.id,
    required this.questionType,
    required this.questionText,
    required this.marks,
    required this.difficulty,
    this.options = const [],
    this.imageUrl,
  });

  factory QuestionModel.fromJson(Map<String, dynamic> json) => QuestionModel(
    id: json['id'] as String,
    questionType: json['question_type'] as String,
    questionText: json['question_text'] as String,
    marks: json['marks'] as int? ?? 1,
    difficulty: json['difficulty'] as String? ?? 'medium',
    options: (json['options'] as List<dynamic>?)
        ?.map((o) => MCQOptionModel.fromJson(o as Map<String, dynamic>))
        .toList() ?? [],
    imageUrl: json['image_url'] as String?,
  );
}

class MCQOptionModel {
  final String id;
  final String label;
  final String text;

  const MCQOptionModel({required this.id, required this.label, required this.text});

  factory MCQOptionModel.fromJson(Map<String, dynamic> json) => MCQOptionModel(
    id: json['id'] as String,
    label: json['option_label'] as String? ?? '',
    text: json['option_text'] as String,
  );
}

class AttemptResult {
  final String id;
  final double score;
  final double percentage;
  final String grade;
  final String comment;
  final int totalMarks;
  final int timeTaken;
  final List<QuestionResult> questionResults;

  const AttemptResult({
    required this.id,
    required this.score,
    required this.percentage,
    required this.grade,
    required this.comment,
    required this.totalMarks,
    required this.timeTaken,
    required this.questionResults,
  });

  factory AttemptResult.fromJson(Map<String, dynamic> json) => AttemptResult(
    id: json['id'] as String,
    score: (json['score'] as num?)?.toDouble() ?? 0.0,
    percentage: (json['percentage'] as num?)?.toDouble() ?? 0.0,
    grade: json['grade'] as String? ?? 'F9',
    comment: json['comment'] as String? ?? '',
    totalMarks: json['total_marks'] as int? ?? 0,
    timeTaken: json['time_taken_seconds'] as int? ?? 0,
    questionResults: (json['question_results'] as List<dynamic>?)
        ?.map((q) => QuestionResult.fromJson(q as Map<String, dynamic>))
        .toList() ?? [],
  );
}

class QuestionResult {
  final String questionId;
  final bool isCorrect;
  final double marksEarned;
  final String? correctAnswer;
  final String? studentAnswer;

  const QuestionResult({
    required this.questionId,
    required this.isCorrect,
    required this.marksEarned,
    this.correctAnswer,
    this.studentAnswer,
  });

  factory QuestionResult.fromJson(Map<String, dynamic> json) => QuestionResult(
    questionId: json['question_id'] as String,
    isCorrect: json['is_correct'] as bool? ?? false,
    marksEarned: (json['marks_earned'] as num?)?.toDouble() ?? 0.0,
    correctAnswer: json['correct_answer'] as String?,
    studentAnswer: json['student_answer'] as String?,
  );
}
