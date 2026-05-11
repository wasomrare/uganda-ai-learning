"""Question bank serializers."""
from rest_framework import serializers
from .models import Question, MCQOption, QuestionAnswer, MatchingPair, FillBlankSegment


class MCQOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCQOption
        fields = ['id', 'option_label', 'option_text', 'option_image', 'is_correct', 'order']


class MCQOptionStudentSerializer(serializers.ModelSerializer):
    """Hides is_correct from students."""
    class Meta:
        model = MCQOption
        fields = ['id', 'option_label', 'option_text', 'option_image', 'order']


class QuestionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = [
            'answer_text', 'answer_keywords', 'explanation',
            'hints', 'marking_guide', 'marking_rubric',
            'minimum_keywords_required',
        ]


class MatchingPairSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchingPair
        fields = ['id', 'left_text', 'right_text', 'left_image', 'right_image', 'order']


class FillBlankSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FillBlankSegment
        fields = ['id', 'segment_text', 'is_blank', 'blank_answer', 'accepted_answers', 'order']


class FillBlankSegmentStudentSerializer(serializers.ModelSerializer):
    """Hides answers from students."""
    class Meta:
        model = FillBlankSegment
        fields = ['id', 'segment_text', 'is_blank', 'order']


class QuestionListSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    topic_name = serializers.CharField(source='topic.name', read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'question_type', 'question_text', 'subject_name', 'topic_name',
            'class_level', 'term', 'difficulty', 'marks', 'source',
            'is_approved', 'use_count', 'correct_rate', 'created_at',
        ]


class QuestionDetailSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    options = MCQOptionSerializer(many=True, read_only=True)
    answer = QuestionAnswerSerializer(read_only=True)
    matching_pairs = MatchingPairSerializer(many=True, read_only=True)
    segments = FillBlankSegmentSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'question_type', 'question_text', 'question_image', 'question_audio',
            'subject', 'subject_name', 'topic', 'topic_name', 'subtopic',
            'class_level', 'term', 'difficulty', 'marks', 'estimated_time_seconds',
            'source', 'ai_model_used', 'is_approved', 'is_active',
            'use_count', 'correct_rate', 'tags', 'learning_objectives',
            'options', 'answer', 'matching_pairs', 'segments', 'created_at',
        ]


class QuestionStudentSerializer(serializers.ModelSerializer):
    """Safe version for students — no answers exposed."""
    options = MCQOptionStudentSerializer(many=True, read_only=True)
    matching_pairs = MatchingPairSerializer(many=True, read_only=True)
    segments = FillBlankSegmentStudentSerializer(many=True, read_only=True)
    hints = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'question_type', 'question_text', 'question_image', 'question_audio',
            'class_level', 'difficulty', 'marks', 'estimated_time_seconds',
            'options', 'matching_pairs', 'segments', 'hints',
        ]

    def get_hints(self, obj):
        if hasattr(obj, 'answer'):
            return obj.answer.hints
        return []


class CreateQuestionSerializer(serializers.ModelSerializer):
    options = MCQOptionSerializer(many=True, required=False)
    answer = QuestionAnswerSerializer(required=False)
    matching_pairs = MatchingPairSerializer(many=True, required=False)
    segments = FillBlankSegmentSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = [
            'question_type', 'subject', 'topic', 'subtopic',
            'class_level', 'term', 'question_text', 'question_image', 'question_audio',
            'marks', 'difficulty', 'estimated_time_seconds',
            'tags', 'learning_objectives', 'options', 'answer',
            'matching_pairs', 'segments',
        ]

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        answer_data = validated_data.pop('answer', None)
        pairs_data = validated_data.pop('matching_pairs', [])
        segments_data = validated_data.pop('segments', [])

        question = Question.objects.create(**validated_data)

        for opt in options_data:
            MCQOption.objects.create(question=question, **opt)
        if answer_data:
            QuestionAnswer.objects.create(question=question, **answer_data)
        for pair in pairs_data:
            MatchingPair.objects.create(question=question, **pair)
        for seg in segments_data:
            FillBlankSegment.objects.create(question=question, **seg)

        return question
