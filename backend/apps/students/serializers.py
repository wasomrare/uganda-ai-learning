"""Student serializers."""
from rest_framework import serializers
from apps.users.serializers import CreateUserSerializer, UserListSerializer
from .models import Student, ParentGuardian, StudentAIProfile


class ParentGuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentGuardian
        fields = ['id', 'full_name', 'relationship', 'phone', 'email', 'occupation', 'address', 'is_primary']


class StudentAIProfileSerializer(serializers.ModelSerializer):
    accuracy_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = StudentAIProfile
        fields = [
            'overall_mastery', 'learning_speed', 'preferred_difficulty',
            'strong_subjects', 'weak_subjects', 'strong_topics', 'weak_topics',
            'learning_style', 'total_questions_attempted', 'total_correct',
            'accuracy_rate', 'current_streak', 'longest_streak',
            'last_activity', 'ple_readiness_score',
        ]


class StudentListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    class_name = serializers.CharField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'admission_number', 'full_name', 'username',
            'class_name', 'stream', 'gender', 'is_active', 'created_at',
        ]


class StudentDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    class_name = serializers.CharField(read_only=True)
    user = UserListSerializer(read_only=True)
    parents = ParentGuardianSerializer(many=True, read_only=True)
    ai_profile = StudentAIProfileSerializer(read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'admission_number', 'full_name', 'user',
            'current_class', 'class_name', 'stream',
            'date_of_birth', 'gender', 'religion',
            'previous_school', 'special_needs', 'photo',
            'enrollment_date', 'is_active',
            'parents', 'ai_profile', 'created_at',
        ]


class CreateStudentSerializer(serializers.Serializer):
    """Creates user account + student profile in one step."""
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    username = serializers.CharField(max_length=150)
    class_id = serializers.UUIDField(required=False)
    stream = serializers.CharField(max_length=10, required=False, default='')
    date_of_birth = serializers.DateField(required=False)
    gender = serializers.ChoiceField(choices=['male', 'female', 'other'], required=False)
    religion = serializers.CharField(max_length=50, required=False, default='')
    parents = ParentGuardianSerializer(many=True, required=False)

    def validate_username(self, value):
        from apps.users.models import User
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists.')
        return value

    def create(self, validated_data):
        from apps.users.models import User
        from apps.classes.models import SchoolClass
        from core.utils import generate_secure_password, generate_admission_number

        parents_data = validated_data.pop('parents', [])
        class_id = validated_data.pop('class_id', None)

        school_class = None
        class_name = 'P1'
        if class_id:
            try:
                school_class = SchoolClass.objects.get(id=class_id)
                class_name = school_class.level
            except SchoolClass.DoesNotExist:
                pass

        password = generate_secure_password()
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role='student',
            password=password,
            force_password_change=True,
        )

        admission_number = generate_admission_number(class_name)
        student = Student.objects.create(
            user=user,
            admission_number=admission_number,
            current_class=school_class,
            stream=validated_data.get('stream', ''),
            date_of_birth=validated_data.get('date_of_birth'),
            gender=validated_data.get('gender', ''),
            religion=validated_data.get('religion', ''),
        )

        StudentAIProfile.objects.create(student=student)

        for parent_data in parents_data:
            ParentGuardian.objects.create(student=student, **parent_data)

        student._temp_password = password
        return student
