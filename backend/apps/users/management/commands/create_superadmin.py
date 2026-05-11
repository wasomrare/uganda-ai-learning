"""Management command to create the initial super admin account."""
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Create initial super admin if none exists.'

    def handle(self, *args, **options):
        from apps.users.models import User
        if User.objects.filter(role='super_admin').exists():
            self.stdout.write(self.style.WARNING('Super admin already exists. Skipping.'))
            return

        user = User.objects.create_superuser(
            username='admin',
            password='Admin@Uganda2024!',
            first_name='System',
            last_name='Administrator',
            role='super_admin',
            is_verified=True,
            force_password_change=True,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Super admin created: username=admin  (please change password immediately)'
        ))
