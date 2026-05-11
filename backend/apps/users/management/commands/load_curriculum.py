"""Load Ugandan UNEB primary curriculum seed data."""
from django.core.management.base import BaseCommand


SUBJECTS = [
    {'name': 'English Language', 'code': 'ENG', 'category': 'language', 'class_levels': ['P1','P2','P3','P4','P5','P6','P7'], 'icon': '📖', 'color': '#3b82f6', 'order': 1},
    {'name': 'Mathematics', 'code': 'MTH', 'category': 'stem', 'class_levels': ['P1','P2','P3','P4','P5','P6','P7'], 'icon': '🔢', 'color': '#8b5cf6', 'order': 2},
    {'name': 'Science', 'code': 'SCI', 'category': 'stem', 'class_levels': ['P4','P5','P6','P7'], 'icon': '🔬', 'color': '#10b981', 'order': 3},
    {'name': 'Social Studies', 'code': 'SST', 'category': 'social', 'class_levels': ['P4','P5','P6','P7'], 'icon': '🌍', 'color': '#f59e0b', 'order': 4},
    {'name': 'Luganda', 'code': 'LUG', 'category': 'language', 'class_levels': ['P1','P2','P3','P4','P5','P6','P7'], 'icon': '🗣️', 'color': '#ef4444', 'order': 5},
    {'name': 'Religious Education', 'code': 'CRE', 'category': 'religious', 'class_levels': ['P1','P2','P3','P4','P5','P6','P7'], 'icon': '✝️', 'color': '#6366f1', 'order': 6},
    {'name': 'Environmental Studies', 'code': 'ENV', 'category': 'social', 'class_levels': ['P1','P2','P3'], 'icon': '🌿', 'color': '#22c55e', 'order': 7},
    {'name': 'Literacy', 'code': 'LIT', 'category': 'language', 'class_levels': ['P1','P2','P3'], 'icon': '📝', 'color': '#06b6d4', 'order': 8},
    {'name': 'Numeracy', 'code': 'NUM', 'category': 'stem', 'class_levels': ['P1','P2','P3'], 'icon': '🔣', 'color': '#a855f7', 'order': 9},
    {'name': 'ICT', 'code': 'ICT', 'category': 'stem', 'class_levels': ['P4','P5','P6','P7'], 'icon': '💻', 'color': '#0ea5e9', 'order': 10},
    {'name': 'Agriculture', 'code': 'AGR', 'category': 'practical', 'class_levels': ['P4','P5','P6','P7'], 'icon': '🌾', 'color': '#84cc16', 'order': 11},
    {'name': 'Reading', 'code': 'RDG', 'category': 'language', 'class_levels': ['P1','P2','P3'], 'icon': '📚', 'color': '#f97316', 'order': 12},
]

SAMPLE_TOPICS = [
    {'subject_code': 'ENG', 'class_level': 'P4', 'term': 1, 'week': 1, 'name': 'Nouns and Pronouns', 'difficulty': 'easy', 'learning_objectives': ['Identify common and proper nouns', 'Use pronouns correctly in sentences'], 'key_vocabulary': ['noun', 'pronoun', 'common', 'proper', 'singular', 'plural']},
    {'subject_code': 'ENG', 'class_level': 'P4', 'term': 1, 'week': 2, 'name': 'Verbs and Tenses', 'difficulty': 'medium', 'learning_objectives': ['Identify action verbs', 'Use past, present and future tenses'], 'key_vocabulary': ['verb', 'tense', 'past', 'present', 'future', 'action']},
    {'subject_code': 'MTH', 'class_level': 'P4', 'term': 1, 'week': 1, 'name': 'Whole Numbers to 10,000', 'difficulty': 'easy', 'learning_objectives': ['Count and write numbers up to 10,000', 'Order numbers in ascending and descending order'], 'key_vocabulary': ['thousands', 'hundreds', 'tens', 'ones', 'place value', 'digit']},
    {'subject_code': 'MTH', 'class_level': 'P4', 'term': 1, 'week': 2, 'name': 'Addition and Subtraction', 'difficulty': 'medium', 'learning_objectives': ['Add 4-digit numbers with carrying', 'Subtract 4-digit numbers with borrowing'], 'key_vocabulary': ['sum', 'difference', 'carry', 'borrow', 'regrouping']},
    {'subject_code': 'SCI', 'class_level': 'P5', 'term': 1, 'week': 1, 'name': 'Living Things', 'difficulty': 'easy', 'learning_objectives': ['Identify characteristics of living things', 'Classify animals and plants'], 'key_vocabulary': ['organism', 'classification', 'vertebrate', 'invertebrate', 'photosynthesis']},
    {'subject_code': 'SST', 'class_level': 'P5', 'term': 1, 'week': 1, 'name': 'Uganda — Our Country', 'difficulty': 'easy', 'learning_objectives': ['Locate Uganda on a map of Africa', 'Identify Uganda\'s neighboring countries'], 'key_vocabulary': ['Uganda', 'capital', 'Kampala', 'borders', 'East Africa', 'Lake Victoria']},
    {'subject_code': 'MTH', 'class_level': 'P7', 'term': 1, 'week': 1, 'name': 'Fractions and Decimals', 'difficulty': 'hard', 'learning_objectives': ['Convert fractions to decimals and percentages', 'Add and subtract fractions with different denominators'], 'key_vocabulary': ['fraction', 'decimal', 'percentage', 'numerator', 'denominator', 'equivalent']},
    {'subject_code': 'ENG', 'class_level': 'P7', 'term': 1, 'week': 1, 'name': 'Comprehension and Summary', 'difficulty': 'hard', 'learning_objectives': ['Read and understand passages', 'Write clear summaries using own words'], 'key_vocabulary': ['comprehension', 'summary', 'inference', 'context', 'main idea']},
]

SAMPLE_BADGES = [
    {'name': 'First Step', 'description': 'Complete your first revision session', 'category': 'academic', 'icon': '👟', 'xp_reward': 50, 'coin_reward': 10, 'rarity': 'common', 'requirement_type': 'revision_sessions', 'requirement_value': {'count': 1}},
    {'name': 'Math Champion', 'description': 'Score 90%+ in Mathematics 5 times', 'category': 'subject', 'icon': '🏆', 'xp_reward': 200, 'coin_reward': 50, 'rarity': 'rare', 'requirement_type': 'subject_score', 'requirement_value': {'subject': 'Mathematics', 'score': 90, 'count': 5}},
    {'name': '7-Day Streak', 'description': 'Study for 7 consecutive days', 'category': 'streak', 'icon': '🔥', 'xp_reward': 150, 'coin_reward': 30, 'rarity': 'rare', 'requirement_type': 'streak', 'requirement_value': {'days': 7}},
    {'name': 'Speed Learner', 'description': 'Complete 10 assessments in one week', 'category': 'speed', 'icon': '⚡', 'xp_reward': 100, 'coin_reward': 25, 'rarity': 'common', 'requirement_type': 'weekly_assessments', 'requirement_value': {'count': 10}},
    {'name': 'Holiday Hero', 'description': 'Complete all holiday revision tasks', 'category': 'holiday', 'icon': '🌟', 'xp_reward': 300, 'coin_reward': 75, 'rarity': 'epic', 'requirement_type': 'holiday_completion', 'requirement_value': {'percentage': 100}},
    {'name': 'PLE Ready', 'description': 'Achieve PLE readiness score above 80%', 'category': 'academic', 'icon': '🎓', 'xp_reward': 500, 'coin_reward': 100, 'rarity': 'legendary', 'requirement_type': 'ple_readiness', 'requirement_value': {'score': 80}},
]


class Command(BaseCommand):
    help = 'Load Uganda UNEB curriculum seed data (subjects, topics, badges).'

    def handle(self, *args, **options):
        self._load_subjects()
        self._load_topics()
        self._load_badges()

    def _load_subjects(self):
        from apps.subjects.models import Subject
        created = 0
        for s in SUBJECTS:
            _, is_new = Subject.objects.update_or_create(code=s['code'], defaults=s)
            if is_new:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Subjects: {created} created / {len(SUBJECTS)} total'))

    def _load_topics(self):
        from apps.curriculum.models import Topic
        from apps.subjects.models import Subject
        created = 0
        for t in SAMPLE_TOPICS:
            subject_code = t.pop('subject_code')
            try:
                subject = Subject.objects.get(code=subject_code)
                _, is_new = Topic.objects.update_or_create(
                    subject=subject, class_level=t['class_level'],
                    term=t['term'], week=t['week'], name=t['name'],
                    defaults={**t, 'subject': subject},
                )
                if is_new:
                    created += 1
            except Subject.DoesNotExist:
                pass
            t['subject_code'] = subject_code
        self.stdout.write(self.style.SUCCESS(f'Topics: {created} created'))

    def _load_badges(self):
        from apps.gamification.models import Badge
        created = 0
        for b in SAMPLE_BADGES:
            _, is_new = Badge.objects.update_or_create(name=b['name'], defaults=b)
            if is_new:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Badges: {created} created'))
