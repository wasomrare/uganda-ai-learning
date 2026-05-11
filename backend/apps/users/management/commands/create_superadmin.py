"""Management command to create the initial super admin account."""
import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create initial super admin if none exists.'

    def handle(self, *args, **options):
        from apps.users.models import User

        username = os.environ.get('ADMIN_USERNAME', 'admin')
        password = os.environ.get('ADMIN_PASSWORD', 'Admin@Uganda2024!')
        email = os.environ.get('ADMIN_EMAIL', 'admin@ugandalearn.com')
        first_name = os.environ.get('ADMIN_FIRST_NAME', 'System')
        last_name = os.environ.get('ADMIN_LAST_NAME', 'Administrator')

        existing = User.objects.filter(role='super_admin').first()
        if existing:
            existing.set_password(password)
            existing.force_password_change = False
            existing.is_active = True
            existing.is_verified = True
            existing.is_staff = True
            existing.is_superuser = True
            existing.save(update_fields=[
                'password', 'force_password_change', 'is_active',
                'is_verified', 'is_staff', 'is_superuser',
            ])
            self.stdout.write(self.style.SUCCESS(
                f'Super admin updated: username={existing.username} (password reset)'
            ))
            return

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
