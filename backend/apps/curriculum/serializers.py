from rest_framework import serializers
from .models import Topic, SubTopic, LearningResource


class SubTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTopic
        fields = ['id', 'name', 'description', 'learning_outcomes', 'difficulty', 'order']


class LearningResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningResource
        fields = ['id', 'title', 'resource_type', 'file', 'url', 'content', 'is_approved', 'download_count']


class TopicListSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subtopic_count = serializers.IntegerField(source='subtopics.count', read_only=True)

    class Meta:
        model = Topic
        fields = [
            'id', 'name', 'subject_name', 'class_level', 'term', 'week',
            'difficulty', 'estimated_mastery_hours', 'subtopic_count', 'order',
        ]


class TopicDetailSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subtopics = SubTopicSerializer(many=True, read_only=True)
    resources = LearningResourceSerializer(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = [
            'id', 'subject', 'subject_name', 'class_level', 'term', 'week',
            'name', 'description', 'learning_objectives', 'competencies',
            'key_vocabulary', 'difficulty', 'estimated_mastery_hours',
            'order', 'subtopics', 'resources', 'created_at',
        ]
