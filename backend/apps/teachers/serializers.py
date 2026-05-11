"""Teacher serializers."""
from rest_framework import serializers
from apps.users.serializers import UserListSerializer
from .models import Teacher


class TeacherListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    class_count = serializers.IntegerField(source='classes.count', read_only=True)
    subject_count = serializers.IntegerField(source='subjects.count', read_only=True)

    class Meta:
        model = Teacher
        fields = [
            'id', 'employee_number', 'full_name', 'username',
            'qualification', 'is_active', 'is_class_teacher',
            'class_count', 'subject_count', 'created_at',
        ]


class TeacherDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    user = UserListSerializer(read_only=True)
    classes = serializers.SerializerMethodField()
    subjects = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = [
            'id', 'employee_number', 'full_name', 'user',
            'qualification', 'specialization', 'experience_years',
            'is_class_teacher', 'is_active', 'bio', 'photo',
            'classes', 'subjects',
            'can_generate_ai_content', 'can_override_ai_marks', 'can_publish_results',
            'created_at',
        ]

    def get_classes(self, obj):
        return [{'id': str(c.id), 'name': c.name} for c in obj.classes.all()]

    def get_subjects(self, obj):
        return [{'id': str(s.id), 'name': s.name} for s in obj.subjects.all()]


class CreateTeacherSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=20, required=False, default='')
    qualification = serializers.CharField(max_length=255, required=False, default='')
    specialization = serializers.CharField(max_length=255, required=False, default='')
    experience_years = serializers.IntegerField(min_value=0, default=0)
    class_ids = serializers.ListField(child=serializers.UUIDField(), required=False)
    subject_ids = serializers.ListField(child=serializers.UUIDField(), required=False)
    can_generate_ai_content = serializers.BooleanField(default=True)
    can_override_ai_marks = serializers.BooleanField(default=True)

    def validate_username(self, value):
        from apps.users.models import User
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists.')
        return value

    def create(self, validated_data):
        from apps.users.models import User
        from apps.classes.models import SchoolClass
        from apps.subjects.models import Subject
        from core.utils import generate_secure_password
        import secrets

        class_ids = validated_data.pop('class_ids', [])
        subject_ids = validated_data.pop('subject_ids', [])

        password = generate_secure_password()
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data.get('email', ''),
            phone=validated_data.get('phone', ''),
            role='teacher',
            password=password,
            force_password_change=True,
        )

        employee_number = f'TCH/{secrets.token_hex(4).upper()}'
        teacher = Teacher.objects.create(
            user=user,
            employee_number=employee_number,
            qualification=validated_data.get('qualification', ''),
            specialization=validated_data.get('specialization', ''),
            experience_years=validated_data.get('experience_years', 0),
            can_generate_ai_content=validated_data.get('can_generate_ai_content', True),
            can_override_ai_marks=validated_data.get('can_override_ai_marks', True),
        )

        if class_ids:
            classes = SchoolClass.objects.filter(id__in=class_ids)
            teacher.classes.set(classes)
        if subject_ids:
            subjects = Subject.objects.filter(id__in=subject_ids)
            teacher.subjects.set(subjects)

        teacher._temp_password = password
        return teacher
