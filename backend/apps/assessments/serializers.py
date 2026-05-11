"""Assessment serializers."""
from rest_framework import serializers
from .models import Assessment, AssessmentAttempt, StudentAnswer, AssessmentQuestion


class AssessmentListSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='school_class.name', read_only=True)
    question_count = serializers.IntegerField(source='questions.count', read_only=True)

    class Meta:
        model = Assessment
        fields = [
            'id', 'title', 'assessment_type', 'class_level', 'class_name',
            'subject_name', 'term', 'total_marks', 'duration_minutes',
            'status', 'is_ai_generated', 'scheduled_start', 'scheduled_end',
            'question_count', 'created_at',
        ]


class AssessmentDetailSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='school_class.name', read_only=True)
    question_count = serializers.IntegerField(source='questions.count', read_only=True)

    class Meta:
        model = Assessment
        fields = [
            'id', 'title', 'description', 'assessment_type',
            'school_class', 'class_level', 'class_name',
            'subject', 'subject_name', 'term', 'academic_year',
            'total_marks', 'passing_marks', 'duration_minutes',
            'shuffle_questions', 'shuffle_options', 'show_results_immediately',
            'allow_review', 'max_attempts', 'status', 'is_ai_generated',
            'scheduled_start', 'scheduled_end', 'instructions',
            'anti_cheat_enabled', 'question_count', 'created_at',
        ]


class StudentAnswerSubmitSerializer(serializers.Serializer):
    question_id = serializers.UUIDField()
    selected_option_id = serializers.UUIDField(required=False)
    text_answer = serializers.CharField(required=False, allow_blank=True)
    matching_answer = serializers.DictField(required=False)
    drag_drop_answer = serializers.ListField(required=False)
    arrangement_answer = serializers.ListField(required=False)
    time_taken_seconds = serializers.IntegerField(required=False, default=0)
    hint_used = serializers.BooleanField(required=False, default=False)


class SubmitAssessmentSerializer(serializers.Serializer):
    answers = StudentAnswerSubmitSerializer(many=True)
    time_taken_seconds = serializers.IntegerField(default=0)


class AttemptResultSerializer(serializers.ModelSerializer):
    assessment_title = serializers.CharField(source='assessment.title', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    grade = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentAttempt
        fields = [
            'id', 'assessment_title', 'student_name', 'attempt_number',
            'status', 'started_at', 'submitted_at', 'time_taken_seconds',
            'ai_score', 'teacher_score', 'final_score', 'percentage',
            'is_passed', 'grade', 'ai_overall_feedback', 'teacher_comment',
        ]

    def get_grade(self, obj):
        from core.utils import get_grade_and_comment
        return get_grade_and_comment(obj.percentage)


class TeacherMarkingSerializer(serializers.Serializer):
    """Teacher overrides AI marks."""
    answer_id = serializers.UUIDField()
    teacher_score = serializers.FloatField()
    teacher_comment = serializers.CharField(required=False, allow_blank=True)
