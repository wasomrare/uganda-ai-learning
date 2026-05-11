"""Management command to create the initial super admin account."""
import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create initial super admin if none exists.'

    def handle(self, *args, **options):
        from apps.users.models import User
        if User.objects.filter(role='super_admin').exists():
            self.stdout.write(self.style.WARNING('Super admin already exists. Skipping.'))
            return

        username = os.environ.get('ADMIN_USERNAME', 'admin')
        password = os.environ.get('ADMIN_PASSWORD', 'Admin@Uganda2024!')
        email = os.environ.get('ADMIN_EMAIL', 'admin@ugandalearn.com')
        first_name = os.environ.get('ADMIN_FIRST_NAME', 'System')
        last_name = os.environ.get('ADMIN_LAST_NAME', 'Administrator')

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='super_admin',
            is_verified=True,
            force_password_change=False,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Super admin created: username={username} email={email}'
        ))
