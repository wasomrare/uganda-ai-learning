from rest_framework import serializers
from .models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = [
            'id', 'name', 'code', 'category', 'class_levels',
            'description', 'icon', 'color', 'is_examinable',
            'is_active', 'order', 'created_at',
        ]
